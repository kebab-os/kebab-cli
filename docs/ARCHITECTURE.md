# Kebab-CLI Architecture

## Overview

Kebab-CLI is a Pygame-based terminal emulator application (v0.1.0) that provides a graphical shell interface with advanced features like text selection, menu system, settings panel, and customizable rendering.

## Core Components

### 1. **TerminalEmulator** (`terminal.py`)
- Main terminal logic and command processing
- Manages input buffer and output buffer
- Handles key events and user input
- Tracks cursor position and text selection
- Maintains terminal running state

### 2. **TerminalRenderer** (`renderer.py`)
- Handles all rendering to the Pygame screen
- Manages font rendering and line height calculations
- Renders output buffer with proper formatting
- Renders menu bar, dropdowns, and UI elements
- Manages settings panel display
- Handles DPI-aware rendering

### 3. **TerminalConfig** (`config.py`)
- Configuration constants for the terminal
- Color scheme definitions
- Terminal behavior settings
- Success and error colors for output

### 4. **Utility Functions** (`utils.py`)
- `strip_ansi()`: Removes ANSI color codes from text for width calculations

## Application Flow

```
boot() → Initialize Pygame → Create Window → Load Assets
         ↓
Create Renderer & Terminal Components
         ↓
Setup Event Handlers & Menu Callbacks
         ↓
Main Event Loop (60 FPS)
         ├─ Event Processing
         ├─ Update Logic (cursor blink, selection)
         ├─ Rendering
         └─ Display Refresh
         ↓
Cleanup & Exit
```

## Key Features

### Input & Output Management
- **Input Buffer**: Captures user keyboard input
- **Output Buffer**: Stores terminal output with formatting
- **Scrolling**: Users can scroll through output history
- **Selection**: Text selection support with mouse interaction

### User Interface
- **Menu Bar**: File, Edit, View, Window menus
- **Settings Panel**: Adjustable font size, line height, colors
- **Custom Cursors**: Pointer and text cursors loaded from static assets
- **Responsive Design**: Handles window resizing

### Event Handling
- **Keyboard Events**: Input processing via `term.handle_key()`
- **Mouse Events**: Menu interaction, text selection, cursor changes
- **Window Events**: Resize handling, quit events
- **Scroll Events**: Mouse wheel scrolling (up/down buttons 4/5)

### File Operations
- **Save Output**: Save terminal output to `output.txt`
- **Save As**: Custom filename selection using Tkinter dialog
- **Clear Output**: Clear all terminal output
- **Storage**: Files saved to `storage/files/` directory

## Directory Structure

```
kebab-cli/
├── kebab_cli.py (entry point)
├── terminal.py (terminal emulator logic)
├── renderer.py (rendering system)
├── config.py (configuration)
├── utils.py (utility functions)
├── input_buffer.py (input management)
├── output_buffer.py (output management)
├── static/
│   └── system/
│       ├── cursor.png (pointer cursor image)
│       ├── cursor-text.png (text cursor image)
│       └── favicon.png (window icon)
├── storage/
│   └── files/ (working directory for file operations)
└── README.md
```

## Configuration & Initialization

### Pygame Setup
- DPI awareness enabled on Windows for proper scaling
- Fullscreen window created with current display dimensions
- Double buffering enabled for smooth rendering
- Custom icon and title set

### Component Initialization
### python
renderer = TerminalRenderer(screen)  # Initialize renderer
term = TerminalEmulator()             # Initialize terminal
###

### Menu System
Menu callbacks are registered for:
- **File**: Save, Save As, Clear
- **Edit**: Copy, Paste (placeholder)
- **View**: Zoom In, Zoom Out (placeholder)
- **Window**: Minimize, Maximize (placeholder)

### Working Directory
Automatically creates and changes to `storage/files/` for file operations.

## Rendering Pipeline

1. **Clear Screen**: `renderer.clear()`
2. **Render Buffer**: Display output with input line
3. **Render Menu Bar**: Display menu labels
4. **Render Dropdown**: Display active menu items
5. **Render Settings**: Button, panel, and close button
6. **Flip Display**: Present to user with `renderer.flip()`

## Event Processing Sequence

### Mouse Motion
1. Check menu hover state
2. Update slider state if settings panel open
3. Check text hover (output/input)
4. Update cursor (text or pointer)
5. Update selection if left button held

### Mouse Button Down
1. Handle menu clicks
2. Check settings panel interactions
3. Process text selection start
4. Handle scroll wheel

### Mouse Button Up
1. End selection
2. Release slider drag

### Keyboard Input
- Routed to `term.handle_key(event)`
- Terminal processes commands internally

### Window Resize
- Update renderer size: `renderer.resize((event.w, event.h))`

## Performance Considerations

- **Frame Rate**: Limited to 60 FPS using `clock.tick(60)`
- **Rendering**: Double buffering prevents flicker
- **Selection Updates**: Only processed when mouse button held
- **Scrolling**: Efficient visible line calculation in `output_buffer.get_visible_with_start()`

## Error Handling

- **File Operations**: Try-catch blocks with user-friendly error messages
- **Windows DPI**: Graceful fallback if DPI awareness not available
- **Asset Loading**: File loading in try-except for robustness
- **Menu Callbacks**: Exception handling prevents crashes from callback errors

## Dependencies

- **pygame**: Windowing, input, rendering
- **datetime**: Timestamp functionality
- **ctypes** (Windows only): DPI awareness
- **tkinter** (optional): File dialog for "Save As"
