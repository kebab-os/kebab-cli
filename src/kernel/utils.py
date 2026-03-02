"""Utility functions"""

import re
import pygame
from .config import TERM_CONFIG


def get_font(size):
    """Load monospace font with fallbacks"""
    fonts = [TERM_CONFIG['font_name']] + TERM_CONFIG['fallback_fonts']
    for font_name in fonts:
        try:
            return pygame.font.SysFont(font_name, size)
        except:
            continue
    return pygame.font.Font(None, size)


def parse_command(line):
    """Parse command line respecting quotes"""
    tokens = []
    current = []
    in_quotes = None
    
    for char in line:
        if char in '"\'':
            if in_quotes == char:
                in_quotes = None
            elif in_quotes is None:
                in_quotes = char
            else:
                current.append(char)
        elif char.isspace() and in_quotes is None:
            if current:
                tokens.append(''.join(current))
                current = []
        else:
            current.append(char)
            
    if current:
        tokens.append(''.join(current))
        
    return tokens


def strip_ansi(text):
    """Remove ANSI escape codes from text"""
    return re.sub(r'\033\[[0-9;]*m', '', text)
