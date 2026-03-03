"""Main entry point for Kebab-CLI"""

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pygame
from datetime import datetime

from .terminal import TerminalEmulator
from .renderer import TerminalRenderer
from .config import TERM_CONFIG
from .utils import strip_ansi

# Load custom cursors
CURSOR_IMAGE = pygame.image.load('static/system/cursor.png')
# scale pointer cursor for visibility and use top-left hotspot (point)
_cursor_scaled = pygame.transform.scale(CURSOR_IMAGE, (16, 24))
_cw, _ch = _cursor_scaled.get_size()
CURSOR = pygame.cursors.Cursor((0, 0), _cursor_scaled)

CURSOR_TEXT_IMAGE = pygame.image.load('static/system/cursor-text.png')
# text cursor (center hotspot)
_cursor_text_scaled = pygame.transform.scale(CURSOR_TEXT_IMAGE, (16, 24))
_tw, _th = _cursor_text_scaled.get_size()
CURSOR_TEXT = pygame.cursors.Cursor((_tw // 2, _th // 2), _cursor_text_scaled)


def boot():
    """Initialize and run the terminal"""
    pygame.init()
    
    # Try to enable DPI awareness on Windows
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Get display info and create window
    info = pygame.display.Info()
    screen = pygame.display.set_mode(
        (info.current_w, info.current_h),
        pygame.RESIZABLE | pygame.DOUBLEBUF
    )

    # Load favicon
    favicon = pygame.image.load('static/system/favicon.png')
    pygame.display.set_icon(favicon)

    # Window Title
    pygame.display.set_caption("Kebab-CLI v0.1.0")
    
    # Set custom cursor
    pygame.mouse.set_cursor(CURSOR)
    
    # Initialize components
    renderer = TerminalRenderer(screen)
    # register menu callbacks which need access to term
    def save_output():
        try:
            path = os.path.join(os.getcwd(), 'output.txt')
            with open(path, 'w', encoding='utf-8') as f:
                for line in term.output_buffer.lines:
                    f.write(strip_ansi(line['text']) + '\n')
            term.output_buffer.add(f"Saved output to {path}", TERM_CONFIG['success_color'])
        except Exception as e:
            term.output_buffer.add(f"Save failed: {e}", TERM_CONFIG['error_color'])
    def save_as():
        # ask for filename via tkinter
        try:
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk(); root.withdraw()
            fname = simpledialog.askstring('Save As', 'Filename:')
            root.destroy()
            if fname:
                path = os.path.join(os.getcwd(), fname)
                with open(path, 'w', encoding='utf-8') as f:
                    for line in term.output_buffer.lines:
                        f.write(strip_ansi(line['text']) + '\n')
                term.output_buffer.add(f"Saved output to {path}", TERM_CONFIG['success_color'])
        except Exception as e:
            term.output_buffer.add(f"Save as failed: {e}", TERM_CONFIG['error_color'])
    def clear_output():
        term.output_buffer.clear()
    renderer.menu_callbacks = {
        'File': {'Save': save_output, 'Save As': save_as, 'Clear': clear_output},
        'Edit': {'Copy': lambda: None, 'Paste': lambda: None},
        'View': {'Zoom In': lambda: None, 'Zoom Out': lambda: None},
        'Window': {'Minimize': lambda: None, 'Maximize': lambda: None},
    }
    # Ensure storage/files exists and make it the current working directory
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage', 'files')
    try:
        os.makedirs(storage_dir, exist_ok=True)
    except Exception:
        pass
    try:
        os.chdir(storage_dir)
    except Exception:
        pass

    term = TerminalEmulator()
    
    # Show welcome message
    term.output_buffer.add("Kebab-CLI v0.1.0 - Shell", TERM_CONFIG['success_color'])
    term.output_buffer.add("Type 'help' for available commands and shortcuts", TERM_CONFIG['prompt_color'])
    term.output_buffer.add("")
    
    clock = pygame.time.Clock()
    
    # Main loop
    running = True
    while running and term.running:
        dt = clock.tick(60)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.VIDEORESIZE:
                renderer.resize((event.w, event.h))
                
            elif event.type == pygame.KEYDOWN:
                term.handle_key(event)
                
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                width_now, height_now = renderer.get_size()
                
                # menu bar hover/interaction
                menu_idx, item_idx = renderer.menu_at_pos((mx, my))
                renderer.hovered_menu_label = menu_idx if item_idx is None else None
                renderer.hovered_menu_item = (menu_idx, item_idx) if item_idx is not None else None
                # if hovering over menu area, don't update text cursor or selection
                over_menu_area = menu_idx is not None
                over_text = False
                pos = None
                
                # Handle settings slider dragging
                if renderer.settings_panel.visible and renderer.settings_panel.dragging_slider is not None:
                    result = renderer.settings_panel.update_slider_from_mouse(mx, width_now)
                    if result:
                        new_value, key = result
                        if key == 'font_size':
                            renderer.update_font_size(new_value)
                        elif key == 'line_height':
                            renderer.update_line_height(new_value)
                        # color keys are updated directly in update_slider_from_mouse
                
                # Update slider hover state
                renderer.settings_panel.handle_mouse_motion((mx, my), width_now, height_now)
                
                if not over_menu_area:
                    # Switch to text cursor when hovering over rendered text
                    # mirror renderer logic: leave top menu bar, extra padding lines, bottom padding and input line
                    usable_height = height_now - 2 * renderer.padding - renderer.menu_bar_height - renderer.top_padding_lines * renderer.line_height - renderer.line_height
                    if usable_height < 0:
                        usable_height = 0
                    visible, start_idx = term.output_buffer.get_visible_with_start(usable_height, renderer.line_height)
                    y_check = renderer.padding + renderer.menu_bar_height + renderer.top_padding_lines * renderer.line_height
                    over_text = False
                    pos = None
                    for i, line_data in enumerate(visible):
                        txt = strip_ansi(line_data['text'])
                        if txt:
                            txt_w = renderer.font.size(txt)[0]
                            if mx >= renderer.padding and mx <= renderer.padding + txt_w and my >= y_check and my < y_check + renderer.line_height:
                                over_text = True
                                # map to absolute line/char
                                rel_char = 0
                                for ci in range(len(txt)+1):
                                    if renderer.font.size(txt[:ci])[0] + renderer.padding > mx:
                                        rel_char = max(0, ci-1)
                                        break
                                pos = {'type': 'output', 'line': start_idx + i, 'char': rel_char}
                            break
                    y_check += renderer.line_height

                # check input/prompt line at bottom (respect bottom padding)
                prompt = term.get_prompt()
                combined = prompt + term.input_buffer.get_text()
                clean_combined = strip_ansi(combined)
                combined_w = renderer.font.size(clean_combined)[0]
                input_y = height_now - renderer.padding - renderer.line_height
                if not over_text and mx >= renderer.padding and mx <= renderer.padding + combined_w and my >= input_y and my < input_y + renderer.line_height:
                    over_text = True
                    # compute char in input+prompt
                    rel_char = 0
                    for ci in range(len(clean_combined)+1):
                        if renderer.font.size(clean_combined[:ci])[0] + renderer.padding > mx:
                            rel_char = max(0, ci-1)
                            break
                    # convert to input-relative char (exclude prompt)
                    prompt_len = len(prompt)
                    input_char = max(0, rel_char - prompt_len)
                    pos = {'type': 'input', 'line': None, 'char': input_char}

                try:
                    if over_text:
                        pygame.mouse.set_cursor(CURSOR_TEXT)
                    else:
                        pygame.mouse.set_cursor(CURSOR)
                except Exception:
                    pass

                # If left mouse button held, update selection
                buttons = getattr(event, 'buttons', (0, 0, 0))
                if buttons[0] and pos and not renderer.settings_panel.dragging_slider:
                    term.update_selection(pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    width_now, height_now = renderer.get_size()
                    # if a menu is open and user clicks outside it, close it
                    if renderer.active_menu is not None:
                        m_idx, i_idx = renderer.menu_at_pos((mx, my))
                        if m_idx is None:
                            renderer.active_menu = None
                            renderer.hovered_menu_item = None
                    # menu click handling
                    menu_idx, item_idx = renderer.menu_at_pos((mx, my))
                    if menu_idx is not None:
                        # label area
                        if item_idx is None:
                            if renderer.active_menu == menu_idx:
                                renderer.active_menu = None
                            else:
                                renderer.active_menu = menu_idx
                            renderer.hovered_menu_item = None
                        else:
                            # execute callback if present
                            menu_label = renderer.menus[menu_idx]['label']
                            menu_item = renderer.menus[menu_idx]['items'][item_idx]
                            cb = renderer.menu_callbacks.get(menu_label, {}).get(menu_item)
                            if cb:
                                try:
                                    cb()
                                except Exception:
                                    pass
                            renderer.active_menu = None
                            renderer.hovered_menu_item = None
                        continue
                    # Check close button click first (highest priority)
                    close_rect = renderer.settings_panel.get_close_button_rect(width_now)
                    if renderer.settings_panel.visible and close_rect.collidepoint((mx, my)):
                        renderer.settings_panel.visible = False
                    # Check settings button click
                    elif renderer.settings_panel.get_button_rect(width_now, renderer.menu_bar_height).collidepoint((mx, my)):
                        renderer.settings_panel.toggle()
                    # Check settings slider click
                    elif renderer.settings_panel.visible:
                        renderer.settings_panel.handle_mouse_down((mx, my), width_now, height_now)
                    # left click -> start selection or place cursor
                    else:
                        usable_height = height_now - 2 * renderer.padding - renderer.menu_bar_height - renderer.top_padding_lines * renderer.line_height - renderer.line_height
                        if usable_height < 0:
                            usable_height = 0
                        visible, start_idx = term.output_buffer.get_visible_with_start(usable_height, renderer.line_height)
                        y_check = renderer.padding + renderer.menu_bar_height + renderer.top_padding_lines * renderer.line_height
                        clicked_pos = None
                        for i, line_data in enumerate(visible):
                            txt = strip_ansi(line_data['text'])
                            if txt:
                                txt_w = renderer.font.size(txt)[0]
                                if mx >= renderer.padding and mx <= renderer.padding + txt_w and my >= y_check and my < y_check + renderer.line_height:
                                    # map to absolute char
                                    rel_char = 0
                                    for ci in range(len(txt)+1):
                                        if renderer.font.size(txt[:ci])[0] + renderer.padding > mx:
                                            rel_char = max(0, ci-1)
                                            break
                                    clicked_pos = {'type': 'output', 'line': start_idx + i, 'char': rel_char}
                                    break
                            y_check += renderer.line_height

                        if not clicked_pos:
                            # check input line with bottom padding
                            prompt = term.get_prompt()
                            combined = prompt + term.input_buffer.get_text()
                            clean_combined = strip_ansi(combined)
                            prompt_len = len(prompt)
                            input_y = height_now - renderer.padding - renderer.line_height
                            if mx >= renderer.padding and mx <= renderer.padding + renderer.font.size(clean_combined)[0] and my >= input_y and my < input_y + renderer.line_height:
                                rel_char = 0
                                for ci in range(len(clean_combined)+1):
                                    if renderer.font.size(clean_combined[:ci])[0] + renderer.padding > mx:
                                        rel_char = max(0, ci-1)
                                        break
                                input_char = max(0, rel_char - prompt_len)
                                clicked_pos = {'type': 'input', 'line': None, 'char': input_char}

                        if clicked_pos:
                            term.start_selection(clicked_pos)
                elif event.button == 4:  # Scroll up
                    if renderer.settings_panel.visible:
                        renderer.settings_panel.scroll(1)
                    else:
                        term.output_buffer.scroll_up()
                elif event.button == 5:  # Scroll down
                    if renderer.settings_panel.visible:
                        renderer.settings_panel.scroll(-1)
                    else:
                        term.output_buffer.scroll_down()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    renderer.settings_panel.handle_mouse_up()
                    term.end_selection()
        
        # Update cursor blink
        term.update_cursor(dt)
        
        # Render
        renderer.clear()
        width, height = renderer.get_size()
        
        # Draw output with input line integrated
        renderer.render_buffer_with_input(
            term.output_buffer,
            height,
            term.get_prompt(),
            term.input_buffer.get_text(),
            term.input_buffer.cursor_pos,
            term.cursor_visible,
            term.get_selection()
        )
        
        # Render menu bar and any open dropdowns, then settings button and panel
        renderer.render_menu_bar(renderer.screen, width)
        renderer.render_dropdown(renderer.screen, renderer.font)
        renderer.settings_panel.render_button(renderer.screen, width, renderer.font, renderer.menu_bar_height)
        renderer.settings_panel.render(renderer.screen, width, height, renderer.font)
        renderer.settings_panel.render_close_button(renderer.screen, width)
        
        renderer.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    boot()
