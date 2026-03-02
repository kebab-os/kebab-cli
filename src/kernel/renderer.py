"""Pygame rendering logic"""

import re
import pygame
from .config import TERM_CONFIG
from .utils import get_font, strip_ansi


class TerminalRenderer:
    """Handles all pygame rendering for the terminal"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = get_font(TERM_CONFIG['font_size'])
        self.line_height = TERM_CONFIG['line_height']
        self.padding = TERM_CONFIG['padding']
        
    def resize(self, size):
        """Handle screen resize"""
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE | pygame.DOUBLEBUF)
        
    def clear(self):
        """Clear screen with background color"""
        self.screen.fill(TERM_CONFIG['bg_color'])
        
    def get_size(self):
        return self.screen.get_size()
        
    def render_buffer(self, buffer, max_height):
        """Render the terminal output buffer"""
        visible_lines = buffer.get_visible(max_height, self.line_height)
        y = self.padding
        
        for line_data in visible_lines:
            text = line_data['text']
            color = line_data['color'] or TERM_CONFIG['fg_color']
            clean_text = strip_ansi(text)
            
            if clean_text:
                surface = self.font.render(clean_text, True, color)
                self.screen.blit(surface, (self.padding, y))
            y += self.line_height
            
        return y
    
    def render_separator(self, y, width):
        """Render line separator between output and input"""
        pygame.draw.line(
            self.screen,
            (60, 60, 60),
            (self.padding, y),
            (width - self.padding, y)
        )
        
    def render_input_line(self, prompt, input_text, cursor_pos, cursor_visible, y):
        """Render the input line with prompt and cursor"""
        # Render prompt
        prompt_surface = self.font.render(prompt, True, TERM_CONFIG['prompt_color'])
        self.screen.blit(prompt_surface, (self.padding, y + 8))
        
        prompt_width = prompt_surface.get_width()
        input_x = self.padding + prompt_width + 5
        
        # Render input text
        input_surface = self.font.render(input_text, True, TERM_CONFIG['fg_color'])
        self.screen.blit(input_surface, (input_x, y + 8))
        
        # Render cursor
        if cursor_visible:
            cursor_x = input_x
            if cursor_pos > 0:
                cursor_text = input_text[:cursor_pos]
                cursor_surface = self.font.render(cursor_text, True, TERM_CONFIG['fg_color'])
                cursor_x += cursor_surface.get_width()
            
            cursor_height = self.line_height - 4
            pygame.draw.rect(
                self.screen,
                TERM_CONFIG['cursor_color'],
                (cursor_x, y + 10, 8, cursor_height)
            )
            
        return input_x
    
    def flip(self):
        """Update display"""
        pygame.display.flip()
