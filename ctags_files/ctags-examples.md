# Ctags Usage Examples

## Quick Reference

### Finding Definitions
```bash
# Search for a specific class
grep "^BoundingBox" tags

# Find all methods of a class
grep "BoundingBox\." tags

# Search for functions
grep "\tf\t" tags

# Search for constants
grep "\tC\t" tags
```

### Using with Vim/Neovim
```vim
" Jump to definition under cursor
Ctrl-]

" Jump back
Ctrl-T

" Search for tag by name
:tag BoundingBox

" Show all tags matching pattern
:tselect Bounding

" Browse tags
:browse tags
```

### Python-Specific Examples

#### Classes in the Project
```
BoundingBox - UI bounding box representation
ImageCanvas - Main image display widget
FullScreenMarkupWindow - Full-screen editing mode
MainWindow - Primary application window
```

#### Key Methods
```
BoundingBox.draw - Render bounding box with handles
ImageCanvas.set_image - Load and analyze image
MainWindow.save_annotations - Export analysis results
```

#### Signals (PyQt6)
```
box_selected - Emitted when bounding box is selected
```

### Editor Shortcuts Summary

| Editor | Jump to Definition | Jump Back | Tag Search |
|--------|-------------------|-----------|------------|
| Vim    | Ctrl-]            | Ctrl-T    | :tag name  |
| Emacs  | M-.               | M-*       | M-x find-tag |
| VS Code| F12 (with ext.)   | Alt-Left  | Ctrl-Shift-P |

### Tag Types Reference

| Type | Meaning | Example |
|------|---------|---------|
| c    | class   | `class BoundingBox:` |
| m    | method  | `def draw(self):` |
| f    | function| `def analyze_ui_elements():` |
| v    | variable| `selected_box = None` |
| C    | constant| `PROJECT_ID = "..."` |
| w    | widget  | `button = QPushButton()` |
| s    | signal  | `box_selected = pyqtSignal()` |
| t    | test    | `def test_bounding_box():` |

## Advanced Usage

### Filtering Tags by File
```bash
# Only show tags from main.py
grep "desktop_analyzer/main.py" tags

# Show only class definitions
grep "\tc\t.*main.py" tags

# Show methods with signatures
grep "\tm\t.*main.py" tags | head -10
```

### Integration with fzf (fuzzy finder)
```bash
# Fuzzy search through all tags
cat tags | fzf

# Search only function names
grep "\tf\t" tags | cut -f1 | fzf
```

### Custom Tag Queries
```bash
# Find all PyQt6 widgets
grep "\tw\t" tags

# Find test functions
grep "\tt\t" tags

# Find signal definitions
grep "\ts\t" tags

# Find constants
grep "\tC\t" tags
```
