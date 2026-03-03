"""Pygame rendering logic"""

import re
import pygame
from .config import TERM_CONFIG
from .utils import get_font, strip_ansi
from .settings import SettingsPanel


class TerminalRenderer:
    """Handles all pygame rendering for the terminal"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = get_font(TERM_CONFIG['font_size'])
        self.line_height = TERM_CONFIG['line_height']
        self.padding = TERM_CONFIG['padding']
        # reserve space for a top menu bar
        self.menu_bar_height = 28
        # leave minimal space below menu bar so first output line isn't obscured
        self.top_padding_lines = 0
        # menu definitions: label and item list
        self.menus = [
            {'label': 'File', 'items': ['Save', 'Save As', 'Clear']},
            {'label': 'Edit', 'items': ['Copy', 'Paste']},
            {'label': 'View', 'items': ['Zoom In', 'Zoom Out']},
            {'label': 'Window', 'items': ['Minimize', 'Maximize']},
        ]
        self.menu_rects = []  # populated during render_menu_bar
        self.active_menu = None  # index of open menu
        self.hovered_menu_label = None  # index of menu label under cursor
        self.hovered_menu_item = None  # (menu_idx, item_idx)
        self.menu_callbacks = {}  # to be filled by caller
        self.settings_panel = SettingsPanel()
    def resize(self, size):
        """Handle screen resize"""
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE | pygame.DOUBLEBUF)
        
    def clear(self):
        """Clear screen with background color"""
        self.screen.fill(TERM_CONFIG['bg_color'])
        
    def get_size(self):
        return self.screen.get_size()
        
    def render_buffer(self, buffer, max_height):
        """Render the terminal output buffer with bottom padding and menu-bar offset"""
        usable_height = max_height - 2 * self.padding - self.menu_bar_height - self.top_padding_lines * self.line_height
        if usable_height < 0:
            usable_height = 0
        visible_lines = buffer.get_visible(usable_height, self.line_height)
        y = self.padding + self.menu_bar_height + self.top_padding_lines * self.line_height

        for line_data in visible_lines:
            text = line_data['text']
            color = line_data['color'] or TERM_CONFIG['fg_color']
            clean_text = strip_ansi(text)

            if clean_text:
                surface = self.font.render(clean_text, True, color)
                self.screen.blit(surface, (self.padding, y))
            y += self.line_height

        return y

    def render_menu_bar(self, screen, screen_width):
        """Draw a simple top menu bar with common menus"""
        bar_rect = pygame.Rect(0, 0, screen_width, self.menu_bar_height)
        pygame.draw.rect(screen, (24, 24, 24), bar_rect)
        # divider line
        pygame.draw.line(screen, (60, 60, 60), (0, self.menu_bar_height - 1), (screen_width, self.menu_bar_height - 1))

        # menu labels
        menu_font = pygame.font.SysFont('consolas', 14)
        x = 10
        self.menu_rects.clear()
        for idx, m in enumerate(self.menus):
            lbl = m['label']
            if self.active_menu == idx or self.hovered_menu_label == idx:
                color = (255, 255, 255)
            else:
                color = (200, 200, 200)
            surf = menu_font.render(lbl, True, color)
            rect = pygame.Rect(x, 0, surf.get_width() + 12, self.menu_bar_height)
            screen.blit(surf, (x + 6, (self.menu_bar_height - surf.get_height()) // 2))
            self.menu_rects.append(rect)
            x += rect.width + 6

    def menu_at_pos(self, pos):
        """Return (menu_idx, item_idx) under mouse pos, or (None,None)"""
        mx, my = pos
        # check labels
        if my <= self.menu_bar_height:
            for idx, rect in enumerate(self.menu_rects):
                if rect.collidepoint(pos):
                    return idx, None
            return None, None
        # check dropdown if open
        if self.active_menu is not None:
            rect = self.menu_rects[self.active_menu]
            font = self.font
            item_height = font.get_height() + 6
            width = max(font.size(it)[0] for it in self.menus[self.active_menu]['items']) + 20
            drop_rect = pygame.Rect(rect.left, rect.bottom, width, item_height * len(self.menus[self.active_menu]['items']))
            if drop_rect.collidepoint(pos):
                rel_y = my - rect.bottom
                item_idx = rel_y // item_height
                if 0 <= item_idx < len(self.menus[self.active_menu]['items']):
                    return self.active_menu, item_idx
        return None, None

    def render_dropdown(self, screen, font):
        """Draw an open dropdown menu if one is active"""
        if self.active_menu is None:
            return
        menu = self.menus[self.active_menu]
        items = menu['items']
        # calculate position under corresponding rect
        rect = self.menu_rects[self.active_menu]
        item_height = font.get_height() + 6
        width = max(font.size(it)[0] for it in items) + 20
        drop_rect = pygame.Rect(rect.left, rect.bottom, width, item_height * len(items))
        pygame.draw.rect(screen, (40, 40, 40), drop_rect)
        pygame.draw.rect(screen, (100, 100, 100), drop_rect, 1)
        for idx, it in enumerate(items):
            item_y = rect.bottom + idx * item_height
            item_rect = pygame.Rect(rect.left, item_y, width, item_height)
            if self.hovered_menu_item == (self.active_menu, idx):
                pygame.draw.rect(screen, (60, 60, 60), item_rect)
            text_surf = font.render(it, True, (220, 220, 220))
            screen.blit(text_surf, (rect.left + 10, item_y + 3))
    
    def render_buffer_with_input(self, buffer, max_height, prompt, input_text, cursor_pos, cursor_visible, selection=None):
        """Render the terminal output buffer with input line integrated at the bottom.
        `selection` should be a tuple (start_pos, end_pos) where each pos is a dict
        {'type':'output'|'input','line':int,'char':int} or None.
        """
        # reduce height to account for padding, menu bar, extra top lines, and input line
        usable_height = max_height - 2 * self.padding - self.menu_bar_height - self.top_padding_lines * self.line_height - self.line_height
        if usable_height < 0:
            usable_height = 0
        visible_lines, start_index = buffer.get_visible_with_start(usable_height, self.line_height)
        y = self.padding + self.menu_bar_height + self.top_padding_lines * self.line_height
        
        # Render all output lines
        # Render all output lines (with selection highlight if present)
        for idx, line_data in enumerate(visible_lines):
            abs_line = start_index + idx
            text = line_data['text']
            color = line_data['color'] or TERM_CONFIG['fg_color']
            clean_text = strip_ansi(text)

            # draw selection background & adjust text color if selection covers this line
            draw_color = color
            if selection:
                sel_a, sel_b = selection
                # output->output selection highlight
                if sel_a['type'] == 'output' and sel_b['type'] == 'output':
                    a_line, a_char = sel_a['line'], sel_a['char']
                    b_line, b_char = sel_b['line'], sel_b['char']
                    if a_line <= abs_line <= b_line:
                        # compute selection range within this line
                        start_char = 0 if abs_line != a_line else a_char
                        end_char = len(clean_text) if abs_line != b_line else b_char
                        if start_char < end_char:
                            pre = clean_text[:start_char]
                            sel = clean_text[start_char:end_char]
                            x = self.padding + (self.font.size(pre)[0] if pre else 0)
                            w = self.font.size(sel)[0]
                            pygame.draw.rect(self.screen, TERM_CONFIG['selection_bg'], (x, y, w, self.line_height))
                        # color text as selected in this range
                        draw_color = TERM_CONFIG['selection_fg']
                # output->input selection (spans from some output line into input)
                elif sel_a['type'] == 'output' and sel_b['type'] == 'input':
                    a_line, a_char = sel_a['line'], sel_a['char']
                    if abs_line >= a_line:
                        start_char = a_char if abs_line == a_line else 0
                        end_char = len(clean_text)
                        if start_char < end_char:
                            pre = clean_text[:start_char]
                            sel = clean_text[start_char:end_char]
                            x = self.padding + (self.font.size(pre)[0] if pre else 0)
                            w = self.font.size(sel)[0]
                            pygame.draw.rect(self.screen, TERM_CONFIG['selection_bg'], (x, y, w, self.line_height))
                        draw_color = TERM_CONFIG['selection_fg']
            # finally render the line text
            surface = self.font.render(clean_text, True, draw_color)
            self.screen.blit(surface, (self.padding, y))
            y += self.line_height
        
        # Render input line with prompt integrated
        prompt_surface = self.font.render(prompt, True, TERM_CONFIG['prompt_color'])
        self.screen.blit(prompt_surface, (self.padding, y))

        prompt_width = prompt_surface.get_width()
        input_x = self.padding + prompt_width

        # Render input text (and selection inside input)
        combined = prompt + (input_text or '')
        clean_combined = strip_ansi(combined)

        # draw selection background if selection covers input
        if selection:
            sel_a, sel_b = selection
            # selection may span from output to input; compute input-relative indices
            if sel_a['type'] == 'input' or sel_b['type'] == 'input' or (sel_a['type'] == 'output' and sel_b['type'] == 'input'):
                # determine input selection start/end in combined string
                if sel_a['type'] == 'input':
                    a_char = sel_a['char'] + len(prompt)
                else:
                    a_char = 0  # selection starts at beginning of input portion
                if sel_b['type'] == 'input':
                    b_char = sel_b['char'] + len(prompt)
                else:
                    b_char = len(clean_combined)
                # clamp within combined
                a_char = max(0, min(len(clean_combined), a_char))
                b_char = max(0, min(len(clean_combined), b_char))
                if a_char < b_char:
                    pre = clean_combined[:a_char]
                    sel = clean_combined[a_char:b_char]
                    x = self.padding + self.font.size(pre)[0]
                    w = self.font.size(sel)[0]
                    pygame.draw.rect(self.screen, TERM_CONFIG['selection_bg'], (x, y, w, self.line_height))
        # render the actual input text after selection highlight
        if input_text:
            input_surface = self.font.render(input_text, True, TERM_CONFIG['fg_color'])
            self.screen.blit(input_surface, (input_x, y))
        # Render cursor
        if cursor_visible:
            cursor_x = input_x
            if cursor_pos > 0:
                cursor_text = input_text[:cursor_pos]
                cursor_surface = self.font.render(cursor_text, True, TERM_CONFIG['fg_color'])
                cursor_x += cursor_surface.get_width()
            
            cursor_height = self.line_height
            pygame.draw.rect(
                self.screen,
                TERM_CONFIG['cursor_color'],
                (cursor_x, y, 1, cursor_height)
            )
    
    def flip(self):
        """Update display"""
        pygame.display.flip()
    
    def update_font_size(self, new_size):
        """Update font size and recalculate line metrics"""
        if 8 <= new_size <= 24:
            self.font = get_font(new_size)
            TERM_CONFIG['font_size'] = new_size
    
    def update_line_height(self, new_height):
        """Update line height"""
        if 12 <= new_height <= 40:
            self.line_height = new_height
            TERM_CONFIG['line_height'] = new_height
