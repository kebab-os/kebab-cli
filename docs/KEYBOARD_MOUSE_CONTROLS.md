# Kebab-CLI Controls Reference

## Keyboard Controls

### Text Input
| Key | Action |
|-----|--------|
| **A-Z, 0-9, symbols** | Type character at cursor position |
| **Enter/Return** | Execute current command |
| **Backspace/Delete** | Remove character before cursor |
| **Tab** | (If implemented) Command completion |
| **Shift+Tab** | (If implemented) Backward completion |

### Navigation
| Key | Action |
|-----|--------|
| **Left Arrow** | Move cursor left |
| **Right Arrow** | Move cursor right |
| **Home** | Move cursor to line start |
| **End** | Move cursor to line end |
| **Up Arrow** | (If implemented) Previous command |
| **Down Arrow** | (If implemented) Next command |
| **Page Up** | (If implemented) Scroll up |
| **Page Down** | (If implemented) Scroll down |

### Selection & Editing
| Key | Action |
|-----|--------|
| **Ctrl+A** | (If implemented) Select all |
| **Ctrl+C** | (If implemented) Copy selection |
| **Ctrl+V** | (If implemented) Paste |
| **Ctrl+X** | (If implemented) Cut |
| **Ctrl+Z** | (If implemented) Undo |

## Mouse Controls

### Position Detection
The application detects mouse position over:
- **Output Text**: Any rendered text from previous commands
- **Input Line**: The active input area with prompt and user text
- **Menu Bar**: Menu labels and items
- **Settings Panel**: Sliders and buttons

### Click Actions

#### Left Click
- **On Text**: Place cursor at clicked position or start selection
- **On Menu Label**: Open/close menu dropdown
- **On Menu Item**: Execute menu action
- **On Settings Button**: Toggle settings panel
- **On Slider**: Start dragging (only when panel visible)
- **On Close Button**: Close settings panel

#### Middle Click
- (Not currently implemented)

#### Right Click
- (Not currently implemented)

### Mouse Motion

| Action | Result |
|--------|--------|
| **Hover over text** | Cursor changes to text cursor (I-beam) |
| **Hover over non-text area** | Cursor changes to pointer cursor |
| **Hover over menu label** | Label highlights |
| **Hover over menu item** | Item highlights |
| **Hold left button + drag** | Create text selection |
| **Drag slider** | Adjust corresponding setting value |

### Scroll Wheel

| Direction | Action |
|-----------|--------|
| **Scroll Up (Button 4)** | Scroll output up (or settings if panel open) |
| **Scroll Down (Button 5)** | Scroll output down (or settings if panel open) |

## Menu Controls

### Opening Menus
1. Click menu label (File, Edit, View, Window)
2. Dropdown appears showing menu items

### Navigating Menus
- Click a menu item to execute action
- Click elsewhere to close menu
- Click same menu label again to close menu

### Available Actions

#### File Menu
```
Save          → Saves output to output.txt
Save As       → Custom filename dialog
Clear         → Clear all output
```

#### Edit Menu
```
Copy          → (Not yet implemented)
Paste         → (Not yet implemented)
```

#### View Menu
```
Zoom In       → (Not yet implemented)
Zoom Out      → (Not yet implemented)
```

#### Window Menu
```
Minimize      → (Not yet implemented)
Maximize      → (Not yet implemented)
```

## Settings Panel Controls

### Opening Settings Panel
1. Click the **Settings** button (right side of menu bar)
2. Panel slides in from the right side

### Adjusting Settings

#### Font Size Slider
- **Drag Left**: Decrease font size (smaller text)
- **Drag Right**: Increase font size (larger text)
- **Real-time Update**: Changes apply immediately

#### Line Height Slider
- **Drag Left**: Decrease line height (tighter spacing)
- **Drag Right**: Increase line height (looser spacing)
- **Real-time Update**: Changes apply immediately

#### Color Sliders (if visible)
- **Adjust RGB Values**: Customize color appearance
- **Real-time Preview**: See changes as you adjust

### Closing Settings Panel
1. Click the **X** button in top-right corner
2. Or click outside the panel (if feature enabled)

## Text Selection

### Mouse Selection
1. Click at start position
2. Hold left mouse button
3. Drag to end position
4. Release to complete selection

### Selection Behavior
- Selection can span multiple lines
- Works in both output text and input line
- Selected text is visually highlighted
- Can be copied (when copy is implemented)

## Cursor Behavior

### Input Cursor
- **Appearance**: Blinking text cursor on input line
- **Position**: Indicates where typed characters will be inserted
- **Blink Rate**: Configured in terminal settings

### Hover Cursor
- **Over Text**: I-beam text cursor
- **Over UI**: Pointer cursor (arrow)
- **Over Menu**: Pointer cursor
- **Over Settings**: Pointer cursor

## Keyboard Shortcuts Summary

```
Quick Reference:
═══════════════════════════════════════════════════════════
Category          | Shortcut              | Function
═══════════════════════════════════════════════════════════
Input             | A-Z, 0-9, Symbols     | Type character
                  | Enter                 | Execute command
                  | Backspace             | Delete character
─────────────────────────────────────────────────────────
Navigation        | ←/→ Arrow             | Move cursor
                  | Home/End              | Line start/end
                  | ↑/↓ Arrow             | History (TBD)
─────────────────────────────────────────────────────────
Scrolling         | Mouse Wheel ↑/↓       | Scroll output
                  | Page Up/Down          | Page scroll (TBD)
─────────────────────────────────────────────────────────
Mouse             | Left Click            | Position cursor
                  | Click + Drag          | Select text
                  | Right Side Button     | Toggle settings
─────────────────────────────────────────────────────────
Menu              | Click Label           | Open menu
                  | Click Item            | Execute action
═══════════════════════════════════════════════════════════
```
