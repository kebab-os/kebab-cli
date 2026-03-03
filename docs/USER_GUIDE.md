# Kebab-CLI User Guide

## Getting Started

### Running the Application

###
bash
python kebab_cli.py
###

The terminal will start in fullscreen mode and display a welcome message:
###
Kebab-CLI v0.1.0 - Shell
Type 'help' for available commands and shortcuts
###

## User Interface

### Menu Bar

Located at the top of the window with the following menus:

#### File Menu
- **Save**: Saves current terminal output to `output.txt` in the current working directory
- **Save As**: Opens a dialog to specify a custom filename for saving
- **Clear**: Clears all terminal output from the display

#### Edit Menu
- **Copy**: (Placeholder for future implementation)
- **Paste**: (Placeholder for future implementation)

#### View Menu
- **Zoom In**: (Placeholder for future implementation)
- **Zoom Out**: (Placeholder for future implementation)

#### Window Menu
- **Minimize**: (Placeholder for future implementation)
- **Maximize**: (Placeholder for future implementation)

### Settings Panel

Click the **Settings** button (located to the right of the menu bar) to open the settings panel.

#### Available Settings

- **Font Size**: Adjust text size (drag slider)
- **Line Height**: Adjust spacing between lines (drag slider)
- **Color Options**: Customize terminal colors (if available)

Close the settings panel by:
- Clicking the **X** button in the top-right corner
- Clicking outside the panel (if implemented)

### Terminal Area

The main content area displays:
- Command output
- Terminal messages
- User input line (at the bottom with prompt)

## Interaction

### Keyboard Input

Type commands directly into the terminal. The cursor appears at the bottom of the screen on the input line.

**Standard shortcuts:**
- **Enter**: Execute command
- **Backspace**: Delete character
- **Left/Right Arrow**: Navigate cursor
- **Up/Down Arrow**: Command history (if implemented)

### Mouse Operations

#### Text Selection
1. Click and drag to select text
2. The cursor changes to a text cursor when hovering over text
3. Selected text is highlighted

#### Menu Interaction
1. Click a menu label to open the dropdown
2. Click a menu item to execute the action
3. Click outside the menu to close it

#### Scrolling
- **Mouse Wheel Up**: Scroll up through output
- **Mouse Wheel Down**: Scroll down through output
- **Scroll in Settings Panel**: Scroll through settings options (if panel is open)

#### Settings Panel
- **Drag Sliders**: Adjust font size, line height, and colors
- **Click Close Button**: Close the panel

### Cursor Behavior

- **Pointer Cursor**: Displayed when not over text
- **Text Cursor**: Displayed when hovering over or in text areas

The cursor blinks while typing in the input line.

## File Operations

### Saving Output

#### Standard Save
1. Click **File** → **Save**
2. Output saves to `output.txt` in your current working directory
3. Confirmation message appears in the terminal

#### Save As
1. Click **File** → **Save As**
2. A dialog appears asking for a filename
3. Enter your desired filename
4. File saves to the working directory
5. Confirmation message appears in the terminal

### Working Directory

The default working directory is `storage/files/` relative to the application installation.

Files are saved with ANSI color codes removed (plain text only).

## Window Management

### Window Sizing
- Double-click the window to maximize/restore
- Drag edges to resize manually
- Application responds to window resize in real-time

### DPI Awareness
- On Windows: Automatic DPI awareness prevents blurriness
- On other systems: Standard Pygame rendering

## Terminal Output

### Color Support
- Success messages appear in green
- Error messages appear in red
- Prompt text appears in configured prompt color
- Regular output appears in white

### ANSI Color Codes
- Internally supported (stripped when saving to file)
- Colors persist in the terminal display

## Tips & Tricks

1. **Selecting Output**: Use mouse to select and copy text from previous commands
2. **Customizing Display**: Use Settings to find your preferred font size and line height
3. **Saving Work**: Regularly save important output to preserve your work
4. **Command History**: If available, use arrow keys to navigate previous commands
5. **Multiple Files**: Use "Save As" to create multiple versions of your terminal session

## Troubleshooting

### Nothing Happens When I Click
- Ensure you're clicking on the correct element
- For menus, click the menu label first to open the dropdown
- For settings, click the Settings button to open the panel

### Text Appears Blurry
- Try adjusting font size in Settings
- Check your display scaling settings

### Can't Find Where Files Were Saved
- Default location: `storage/files/` in the application directory
- Use "Save As" to save to a specific location

### Settings Panel Won't Close
- Click the **X** button in the top-right corner of the panel
- Try clicking outside the panel
