"""Terminal configuration constants"""

TERM_CONFIG = {
    'font_size': 14,
    'font_name': 'Consolas',
    'fallback_fonts': ['DejaVu Sans Mono', 'Liberation Mono', 'Courier New', 'Monospace'],
    'bg_color': (30, 30, 30),
    'fg_color': (240, 240, 240),
    'cursor_color': (0, 255, 0),
    'prompt_color': (0, 184, 148),
    'error_color': (255, 100, 100),
    'success_color': (100, 255, 100),
    'padding': 10,
    'line_height': 20,
    'cursor_blink_ms': 530,
    'history_file': '.kebab_history',
    'max_history': 1000,
    'scrollback_lines': 500
}

# Selection colors
TERM_CONFIG['selection_bg'] = (60, 120, 200)
TERM_CONFIG['selection_fg'] = (255, 255, 255)
