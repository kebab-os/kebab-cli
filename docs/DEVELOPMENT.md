# Kebab-CLI Development Guide

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                   kebab_cli.py                       │
│                (Main Entry Point)                    │
└─────────────────────────┬────────────────────────────┘
                          │
        ┌─────────────────┴────────────────┐
        │                                  │
┌───────▼──────────┐             ┌─────────▼─────────┐
│ TerminalEmulator │             │  TerminalRenderer │
│      (Logic)     │             │     (Display)     │
└───────┬──────────┘             └─────────┬─────────┘
        │                                  │
        │          ┌─────────────────────┬─┘
        │          │                     │
    ┌───▼──────────▼────┐    ┌───────────▼──┐
    │  Input/Output     │    │ Settings     │
    │   Buffers         │    │ Panel        │
    └───────────────────┘    └──────────────┘
```

## Module Descriptions

### `kebab_cli.py`
**Purpose**: Application entry point and main event loop

**Key Functions**:
- `boot()`: Initialize and run the application
- Event handling for keyboard, mouse, window events
- Main render loop at 60 FPS
- Menu callback definitions

**Key Variables**:
- `CURSOR`: Default pointer cursor
- `CURSOR_TEXT`: Text input cursor
- `renderer`: TerminalRenderer instance
- `term`: TerminalEmulator instance
- `screen`: Pygame display surface

### `terminal.py`
**Purpose**: Terminal emulator logic

**Key Classes**:
- `TerminalEmulator`: Main terminal class

**Key Methods** (implement these):
- `handle_key(event)`: Process keyboard input
- `update_cursor(dt)`: Update cursor blink state
- `update_selection(pos)`: Handle text selection
- `start_selection(pos)`: Begin selection
- `end_selection()`: Complete selection
- `get_selection()`: Return selected text
- `get_prompt()`: Return current prompt string
- `run_command(cmd)`: Execute user command

**Key Properties**:
- `output_buffer`: OutputBuffer instance
- `input_buffer`: InputBuffer instance
- `cursor_visible`: Boolean for cursor blink state
- `running`: Boolean for application state

### `renderer.py`
**Purpose**: All rendering and UI display

**Key Classes**:
- `TerminalRenderer`: Main renderer class
- `SettingsPanel`: Settings UI panel

**Key Methods** (implement these):
- `clear()`: Clear screen
- `flip()`: Display to screen
- `resize(size)`: Handle window resize
- `render_buffer_with_input()`: Render output + input
- `render_menu_bar()`: Draw menu bar
- `render_dropdown()`: Draw active menu
- `update_font_size(size)`: Change font
- `update_line_height(height)`: Change spacing
- `get_size()`: Return screen dimensions
- `font.size(text)`: Calculate text width
- `menu_at_pos(pos)`: Get menu at mouse position

**Key Properties**:
- `screen`: Pygame Surface
- `font`: Pygame font object
- `padding`: Screen padding in pixels
- `line_height`: Height between text lines
- `menu_bar_height`: Height of menu bar
- `menus`: List of menu definitions
- `menu_callbacks`: Dict of menu actions
- `settings_panel`: SettingsPanel instance

### `config.py`
**Purpose**: Configuration constants

**Key Configuration**:
- `TERM_CONFIG`: Dictionary with colors and settings

```python
TERM_CONFIG = {
    'success_color': (0, 255, 0),
    'error_color': (255, 0, 0),
    'prompt_color': (100, 149, 237),
    'default_color': (255, 255, 255),
    'background_color': (0, 0, 0),
}
```

### `utils.py`
**Purpose**: Utility functions

**Key Functions**:
- `strip_ansi(text)`: Remove ANSI color codes

### `input_buffer.py`
**Purpose**: Handle user input

**Key Classes**:
- `InputBuffer`: Text input buffer

**Key Methods** (implement these):
- `add_char(char)`: Insert character
- `remove_char()`: Delete character
- `get_text()`: Return buffer contents
- `clear()`: Clear buffer
- `move_cursor(offset)`: Change cursor position

**Key Properties**:
- `cursor_pos`: Current cursor position
- `buffer`: Internal text storage

### `output_buffer.py`
**Purpose**: Manage terminal output

**Key Classes**:
- `OutputBuffer`: Output buffer with scrolling

**Key Methods** (implement these):
- `add(text, color)`: Add line to buffer
- `clear()`: Clear all output
- `scroll_up()`: Scroll up
- `scroll_down()`: Scroll down
- `get_visible_with_start(height, line_height)`: Get visible lines

**Key Properties**:
- `lines`: List of line dictionaries
- `scroll_pos`: Current scroll position
- `lines[i]['text']`: Text of line i
- `lines[i]['color']`: Color of line i

## Key Code Sections

### Mouse Position Detection

```python
# Output text region
usable_height = height_now - 2 * renderer.padding - ...
visible, start_idx = term.output_buffer.get_visible_with_start(
    usable_height, renderer.line_height
)

# Input line region
prompt = term.get_prompt()
combined = prompt + term.input_buffer.get_text()
input_y = height_now - renderer.padding - renderer.line_height
```

### Text Width Calculation

```python
txt = strip_ansi(line_data['text'])
txt_w = renderer.font.size(txt)[0]
# Character position detection
for ci in range(len(txt)+1):
    if renderer.font.size(txt[:ci])[0] + renderer.padding > mx:
        rel_char = max(0, ci-1)
        break
```

### Event Loop Structure

```python
running = True
while running and term.running:
    dt = clock.tick(60)  # 60 FPS cap
    
    for event in pygame.event.get():
        # Handle events
        
    # Update logic
    term.update_cursor(dt)
    
    # Render
    renderer.clear()
    renderer.render_buffer_with_input(...)
    renderer.render_menu_bar(...)
    renderer.flip()
```

## Adding New Features

### Adding a Menu Item

1. **Update menu definition** in `renderer.py`:
```python
self.menus = [
    {'label': 'File', 'items': ['Save', 'Save As', 'Clear', 'New Item']}
]
```

2. **Add callback** in `kebab_cli.py`:
```python
def new_feature():
    term.output_buffer.add("Feature executed!", TERM_CONFIG['success_color'])

renderer.menu_callbacks = {
    'File': {
        'Save': save_output,
        'Save As': save_as,
        'Clear': clear_output,
        'New Item': new_feature
    }
}
```

### Adding a Settings Control

1. **Create slider definition** in `SettingsPanel`:
```python
self.sliders = [
    {'key': 'font_size', 'label': 'Font Size', 'min': 8, 'max': 32, 'value': 14},
    {'key': 'new_setting', 'label': 'New Setting', 'min': 0, 'max': 100, 'value': 50}
]
```

2. **Handle slider update** in mouse motion event:
```python
if key == 'new_setting':
    # Apply setting
    renderer.update_setting(new_value)
```

### Adding Keyboard Shortcuts

In `terminal.py` `handle_key()` method:
```python
if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
    # Handle Ctrl+S
    self.output_buffer.add("Ctrl+S pressed!", color)
```

## Common Patterns

### Displaying Output
```python
term.output_buffer.add("Message text", TERM_CONFIG['success_color'])
term.output_buffer.add("Error occurred", TERM_CONFIG['error_color'])
```

### Getting Mouse Position
```python
mx, my = event.pos
width_now, height_now = renderer.get_size()
```

### Checking if Point in Rectangle
```python
rect = pygame.Rect(x, y, w, h)
if rect.collidepoint((mx, my)):
    # Point is in rectangle
```

### Converting Mouse Position to Text Position
```python
txt = strip_ansi(line_text)
txt_width = renderer.font.size(txt)[0]
if mx >= renderer.padding and mx <= renderer.padding + txt_width:
    # Mouse is over text, find character
    for ci in range(len(txt)+1):
        if renderer.font.size(txt[:ci])[0] + renderer.padding > mx:
            char_pos = max(0, ci-1)
            break
```

## Testing

### Unit Testing Template

```python
# test_terminal.py
import unittest
from terminal import TerminalEmulator

class TestTerminalEmulator(unittest.TestCase):
    def setUp(self):
        self.term = TerminalEmulator()
    
    def test_input_buffer(self):
        self.term.input_buffer.add_char('a')
        self.assertEqual(self.term.input_buffer.get_text(), 'a')
    
    def test_output_buffer(self):
        self.term.output_buffer.add("Test", (255, 255, 255))
        self.assertGreater(len(self.term.output_buffer.lines), 0)

if __name__ == '__main__':
    unittest.main()
```

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Window can be resized
- [ ] Menu clicks work
- [ ] File operations work
- [ ] Settings panel opens/closes
- [ ] Text selection works
- [ ] Scrolling works
- [ ] Keyboard input works
- [ ] Mouse cursor changes correctly

## Performance Optimization

### Rendering Optimization
- Only render visible lines
- Cache font size calculations
- Use double buffering (already implemented)

### Input Optimization
- Debounce slider updates
- Batch text rendering operations
- Limit selection updates to when button held

### Memory Optimization
- Limit output buffer size
- Clear old selection data
- Unload unused assets

## Debugging Tips

### Enable Debug Output
```python
# Add to kebab_cli.py
import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In event handlers
logger.debug(f"Event type: {event.type}, Position: {event.pos}")
```

### Common Issues

1. **Cursor position incorrect**
   - Check `strip_ansi()` is called before width calculation
   - Verify coordinate system (screen space vs text space)

2. **Menu not responding**
   - Check menu label exact match in callbacks dict
   - Verify callback is not None
   - Add try-catch to see exceptions

3. **Rendering artifacts**
   - Ensure `renderer.clear()` called before rendering
   - Check for overlapping UI elements
   - Verify double buffering is enabled
