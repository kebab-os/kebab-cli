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
    pygame.display.set_caption("Kebab-CLI v1.0")
    
    # Initialize components
    renderer = TerminalRenderer(screen)
    term = TerminalEmulator()
    
    # Show welcome message
    term.output_buffer.add("Kebab-CLI v1.0 - Pygame Terminal Emulator", TERM_CONFIG['success_color'])
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
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    term.output_buffer.scroll_up()
                elif event.button == 5:  # Scroll down
                    term.output_buffer.scroll_down()
        
        # Update cursor blink
        term.update_cursor(dt)
        
        # Render
        renderer.clear()
        width, height = renderer.get_size()
        
        # Calculate layout
        input_area_height = TERM_CONFIG['line_height'] + 10
        output_height = height - input_area_height - TERM_CONFIG['padding'] * 2
        
        # Draw output
        renderer.render_buffer(term.output_buffer, output_height)
        
        # Draw separator and input
        input_y = height - input_area_height - TERM_CONFIG['padding']
        renderer.render_separator(input_y, width)
        renderer.render_input_line(
            term.get_prompt(),
            term.input_buffer.get_text(),
            term.input_buffer.cursor_pos,
            term.cursor_visible,
            input_y
        )
        
        renderer.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    boot()
