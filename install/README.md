# kebab-cli Developer Documentation

## Quick Setup

### Windows (PowerShell as Administrator)
```powershell
cd ~
if (!(Test-Path .kebab)) { mkdir .kebab }
cd .kebab
curl.exe -L https://github.com/kebab-os/kebab-cli/archive/refs/heads/main.zip -o kebab-cli.zip
Expand-Archive -Path kebab-cli.zip -DestinationPath . -Force
cd kebab-cli/src
```

### Linux
```bash
cd ~
mkdir .kebab
cd .kebab
git clone https://github.com/kebab-os/kebab-cli.git
cd kebab-cli/src
sudo apt-get install xclip  # Debian/Ubuntu
# For other distros:
# sudo pacman -S xclip      # Arch
# sudo dnf install xclip    # Fedora
```

### macOS
```bash
cd ~
mkdir .kebab
cd .kebab
git clone https://github.com/kebab-os/kebab-cli.git
cd kebab-cli/src
# Ensure Xcode command line tools are installed:
# xcode-select --install
```

---

## Installation Scripts

- **Windows**: `windows.sh`
- **Linux**: `linux.sh`
- **macOS**: `mac.sh`

---

## Documentation Index

### 🚀 Getting Started
- Installation & Setup - System requirements, dependencies, install steps, folder layout, and troubleshooting
- Quick Start Guide - First steps after installation

### 📚 User Documentation
- User Guide - Menus, settings panel, selection, saving output, window behavior, and troubleshooting
- Keyboard & Mouse Controls - Quick reference for input, navigation, selection, scrolling, and menu interactions

### 🔧 Developer Documentation
- Architecture Overview - Core components, event flow, rendering pipeline, and key design decisions
- Development Guide - Module breakdown, patterns, testing, debugging tips, and adding new features
- API Reference - Public APIs, events, and extension points
- Building from Source - Compilation options, build flags, and packaging

### 📖 Reference
- Configuration File - All available settings and their defaults
- Command Line Options - Complete list of CLI flags and arguments
- FAQ - Frequently asked questions
- Troubleshooting - Common issues and solutions

### 🤝 Contributing
- Contributing Guidelines - How to submit issues, feature requests, and PRs
- Code of Conduct
- Style Guide - Coding standards and conventions

---

## Development Setup

### Prerequisites
- **C++17** compatible compiler (g++ 7+, clang 6+, MSVC 2017+)
- **CMake** 3.10 or higher
- **Git** (for cloning)
- **xclip** (Linux) or **Xcode CLT** (macOS) for clipboard support

### Building from Source

```bash
# Clone the repository
git clone https://github.com/kebab-os/kebab-cli.git
cd kebab-cli

# Create build directory
mkdir build && cd build

# Configure with CMake
cmake .. -DCMAKE_BUILD_TYPE=Debug  # or Release

# Build
cmake --build . --parallel 4

# Run tests (optional)
ctest --output-on-failure
```


### Development Workflow

1. **Fork & Clone** the repository
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following the style guide
4. **Write/update tests** for new functionality
5. **Run the test suite** to ensure everything passes
6. **Commit** with clear, descriptive messages
7. **Push** to your fork and open a Pull Request

### Debugging Tips

**Enable debug logging:**
```bash
./kebab-cli --debug  # or -d
```

**Use GDB/lldb:**
```bash
gdb ./kebab-cli
(gdb) run
(gdb) bt  # backtrace on crash
```

**Valgrind (Linux) for memory issues:**
```bash
valgrind --leak-check=full ./kebab-cli
```

**AddressSanitizer (build with):**
```bash
cmake .. -DCMAKE_BUILD_TYPE=Debug -DSANITIZE_ADDRESS=ON
```

---

## Key Design Decisions

- **Modular architecture** with clear separation of concerns
- **Event-driven** input handling
- **Double-buffered rendering** for smooth output
- **Cross-platform compatibility** (Windows/Linux/macOS)
- **Minimal dependencies** for easy building

---

## Need Help?

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Discord**: kebabOS Discord
- **Twitter**: @kebab_os

<br /><br />

---

<div align="right">
  <sub>kebab-cli</sub>
</div>
