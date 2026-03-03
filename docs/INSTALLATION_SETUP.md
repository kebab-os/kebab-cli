# Kebab-CLI Installation & Setup

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 512MB (1GB recommended)
- **Display**: Any resolution (fullscreen native resolution recommended)

## Dependencies

### Required
###
pygame>=2.0.0      # Window management and rendering
###

### Optional
###
tkinter            # For "Save As" file dialog (usually included with Python)
###

## Installation

### 1. Clone or Download the Repository

###
bash
git clone https://github.com/yourusername/kebab-cli.git
cd kebab-cli
###

### 2. Create Virtual Environment (Recommended)

**Windows:**
###
bash
python -m venv venv
venv\Scripts\activate
###

**macOS/Linux:**
###
bash
python3 -m venv venv
source venv/bin/activate
###

### 3. Install Dependencies

###
bash
pip install pygame
###

### 4. Verify Installation

###
bash
python -c "import pygame; print(f'Pygame {pygame.version.ver} installed successfully')"
###

## Project Structure Setup

Ensure the following directory structure exists:

###
kebab-cli/
├── kebab_cli.py              (main entry point)
├── terminal.py               (terminal emulator)
├── renderer.py               (rendering system)
├── config.py                 (configuration)
├── utils.py                  (utilities)
├── input_buffer.py           (input handling)
├── output_buffer.py          (output handling)
├── static/
│   └── system/
│       ├── cursor.png        (pointer cursor image)
│       ├── cursor-text.png   (text cursor image)
│       └── favicon.png       (window icon)
├── storage/
│   └── files/                (working directory - auto-created)
├── requirements.txt          (optional)
└── README.md
###

### Auto-Created Directories

The following directories are automatically created on first run:
- `storage/files/` - Default working directory for file operations

## Running the Application

### Standard Execution

###
bash
python kebab_cli.py
###

The application will:
1. Initialize Pygame
2. Create a fullscreen window
3. Load custom cursors and favicon
4. Display the welcome message
5. Ready for input

### Troubleshooting Startup Issues

#### "ModuleNotFoundError: No module named 'pygame'"
###
bash
# Make sure pygame is installed
pip install pygame

# Or reinstall if corrupted
pip install --upgrade --force-reinstall pygame
###

#### "ModuleNotFoundError: No module named 'terminal'"
###
bash
# Make sure you're in the correct directory with all modules
ls -la  # or dir (on Windows)

# Verify the file exists
python -c "from kebab_cli import *"
###

#### "Cannot find image file 'static/system/cursor.png'"
- Ensure you're running from the correct directory
- Check that `static/` directory exists with all required PNG files
- File paths are relative to the script execution location

#### "pygame.error: No available video device"
- This is a display server issue (common on headless/SSH systems)
- Solution: Install a display driver or use X11 forwarding

## Configuration

### Settings File (Optional)

Create `config.py` if it doesn't exist with default values:

### python
TERM_CONFIG = {
    'success_color': (0, 255, 0),      # Green
    'error_color': (255, 0, 0),        # Red
    'prompt_color': (100, 149, 237),   # Cornflower blue
    'default_color': (255, 255, 255),  # White
    'background_color': (0, 0, 0),     # Black
    'font_name': 'monospace',
    'font_size': 14,
    'line_height': 20,
}
###

### Environment Variables

Optional environment variables:

###
bash
# Set custom working directory
export KEBAB_WORK_DIR=/path/to/directory
python kebab_cli.py

# Set custom font (if implemented)
export KEBAB_FONT="Courier New"
python kebab_cli.py
###

## Asset Files

### Required Image Assets

Place these files in `static/system/`:

1. **cursor.png** (16x24 pixels recommended)
   - Standard pointer cursor
   - Hotspot: (0, 0) - top-left

2. **cursor-text.png** (16x24 pixels recommended)
   - Text/I-beam cursor
   - Hotspot: (8, 12) - center

3. **favicon.png** (32x32 or 64x64 pixels)
   - Window icon
   - Recommended: High contrast for visibility

### Creating Custom Cursors

To create custom cursor images:

1. Design 24x24 pixel PNG images
2. Use transparent background
3. Place hotspot coordinates carefully
4. Save to `static/system/`

PNG files must be RGBA format with transparency support.

## Post-Installation Verification

### Quick Test

###
bash
python -c "
import sys
sys.path.insert(0, '.')
try:
    from kebab_cli import boot
    print('✓ Module imports successful')
    print('✓ Ready to run: python kebab_cli.py')
except Exception as e:
    print(f'✗ Error: {e}')
"
###

### Full Startup Test

###
bash
python kebab_cli.py &
sleep 2
pkill -f kebab_cli.py
echo "✓ Application started and stopped successfully"
###

## Platform-Specific Notes

### Windows
- **DPI Awareness**: Automatically enabled (Windows 10+)
- **Fonts**: Ensure monospace font is installed (Consolas, Courier New)
- **File Paths**: Backslashes handled automatically

### macOS
- **Fullscreen**: May behave differently on M1/M2 Macs
- **Fonts**: Use Monaco or Courier New
- **Permissions**: May need terminal app permissions

### Linux
- **Display Server**: X11 or Wayland required
- **Fonts**: Install Liberation Mono or Ubuntu Mono
- **Dependencies**: May need: `sudo apt-get install python3-tk python3-pygame`

## Uninstallation

### Remove Application

###
bash
# Remove the directory
rm -rf kebab-cli

# Or on Windows
rmdir /s kebab-cli
###

### Remove Virtual Environment

###
bash
# Deactivate first
deactivate

# Remove
rm -rf venv

# Or on Windows
rmdir /s venv
###

## Getting Help

### Debug Mode

Add this to `kebab_cli.py` for debug output:

### python
import logging
logging.basicConfig(level=logging.DEBUG)
###

### Check Logs

After running, check for any error messages in terminal output.

### Reporting Issues

When reporting issues, include:
- Python version: `python --version`
- Pygame version: `pip show pygame`
- Operating system and version
- Complete error message
- Steps to reproduce
