# Ctags Configuration

This directory contains configuration files for Universal Ctags to provide enhanced code navigation for the Desktop UI/UX Analyzer project.

## Files

- **`config.ctags`** - Main configuration with exclusions and general settings
- **`python.ctags`** - Python-specific enhancements for PyQt6 development
- **`update_ctags.sh`** - Script to generate and update ctags
- **`Makefile`** - Make targets for ctags management
- **`README.md`** - This documentation file

## Quick Start

From the project root:

```bash
# Generate tags (multiple ways)
./update_ctags.sh
make -f ctags_files/Makefile ctags
ctags -R .

# With verbose output
./update_ctags.sh --verbose

# Clean tags
make -f ctags_files/Makefile clean
```

## Features

### Python Support

- ✅ Standard Python elements (classes, functions, methods, variables)
- ✅ PyQt6 widgets detection (type `w`)
- ✅ PyQt6 signals detection (type `s`)
- ✅ Test functions identification (type `t`)
- ✅ Constants detection (type `C`)
- ✅ Enhanced method signatures with type hints

### File Exclusions

Automatically excludes common build artifacts and cache directories:

- Python: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`
- Build tools: `build/`, `dist/`, `.tox/`
- IDEs: `.idea/`, `.vscode/`
- Version control: `.git/`

### Project-Specific

Configured for this PyQt6 desktop application with special handling for:

- UI component classes
- Signal/slot patterns
- Event handlers
- Custom widget implementations

## Usage

The configuration is automatically loaded by ctags when run from the project root:

```bash
# Generate tags (uses configuration automatically)
ctags -R .

# Or use project scripts
./update_ctags.sh
make ctags
```

## Tag Types

| Type | Description | Example |
|------|-------------|---------|
| `c` | Class | `class BoundingBox:` |
| `m` | Method | `def draw(self):` |
| `f` | Function | `def analyze_ui_elements():` |
| `v` | Variable | `selected_box = None` |
| `C` | Constant | `PROJECT_ID = "..."` |
| `w` | Widget | `button = QPushButton()` |
| `s` | Signal | `box_selected = pyqtSignal()` |
| `t` | Test | `def test_bounding_box():` |

## Maintenance

Configuration files are version controlled and automatically applied. No manual setup required for new developers.

For issues or enhancements, modify the appropriate `.ctags` file and test with:

```bash
ctags --verbose -R .
```
