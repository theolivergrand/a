# Ctags Configuration Guide

## Overview
This project uses Universal Ctags for code navigation and analysis. The configuration is optimized for Python development with PyQt6.

## Configuration Files

### `.ctags.d/config.ctags`
Main configuration file with:
- Recursive scanning (`--recurse=yes`)
- Relative tag paths (`--tag-relative=yes`)
- Exclusion patterns for build artifacts, cache files, etc.
- Extended field information (`--fields=+iaS`)
- Additional qualified tags (`--extras=+q`)

### `.ctags.d/python.ctags`
Python-specific enhancements:
- PyQt6 widget detection (`w` type for widgets)
- PyQt6 signal detection (`s` type for signals)
- Test function identification (`t` type for test functions)
- Constant detection (`C` type for constants)

## Usage

### Command Line
```bash
# Generate tags for the entire project
ctags -R --fields=+iaS --extras=+q --output-format=e-ctags .

# Use the provided script for enhanced output
./update_ctags.sh

# Verbose mode for debugging
./update_ctags.sh --verbose
```

### VS Code Tasks
Use the configured tasks in VS Code:
- **Generate ctags**: Basic tag generation
- **Generate ctags (verbose)**: Detailed output for debugging
- **Clean ctags**: Remove existing tags file

### Tag Statistics
Current project generates approximately 200+ tags including:
- Classes and methods from Python modules
- PyQt6 widgets and signals
- Function definitions
- Constants and variables
- Markdown sections

## Editor Integration

### Vim/Neovim
- `Ctrl-]`: Jump to definition
- `Ctrl-T`: Jump back
- `:tag <name>`: Search for specific tag
- `:tags`: Show tag stack

### VS Code
Install a ctags extension for navigation support:
- "ctags support" extension
- "Tags" extension

### Emacs
Use built-in etags support or packages like:
- `ggtags`
- `counsel-etags`

## File Types Supported
- Python (`.py`, `.pyi`)
- Markdown (`.md`)
- JSON (basic support)

## Exclusions
The following directories and files are excluded:
- `.git`, `__pycache__`, `*.pyc`
- `venv`, `.venv`, `node_modules`
- Build artifacts: `build/`, `dist/`, `*.egg-info/`
- IDE files: `.idea/`, `.vscode/`
- Test artifacts: `.tox/`, `.pytest_cache/`
- Documentation builds: `docs/_build/`

## Maintenance
- Tags are automatically excluded from version control via `.gitignore`
- Run `./update_ctags.sh` after significant code changes
- The script provides statistics and recent tag summaries

## Troubleshooting

### Common Issues
1. **"ctags: command not found"**
   ```bash
   sudo apt-get install universal-ctags
   ```

2. **"Language already defined" errors**
   - Check for duplicate language definitions in `.ctags.d/`
   - Ensure custom language names don't conflict with built-ins

3. **Empty or incomplete tags**
   - Check file permissions
   - Verify exclusion patterns aren't too broad
   - Use verbose mode for debugging

### Debug Commands
```bash
# Test ctags on a single file
ctags --fields=+iaS --extras=+q desktop_analyzer/main.py

# List supported languages
ctags --list-languages

# Show configuration
ctags --list-options

# Verbose parsing
ctags --verbose -R .
```

## Performance
- Tag generation typically takes 1-2 seconds for this project
- Tags file size: ~27KB for current codebase
- Memory usage: minimal impact on editors
