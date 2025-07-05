# Makefile for Desktop UI/UX Analyzer project

.PHONY: help ctags ctags-verbose ctags-clean ctags-watch install lint test run docs

# Default target
help:
	@echo "Available targets:"
	@echo "  ctags         - Generate ctags for the project"
	@echo "  ctags-verbose - Generate ctags with verbose output"
	@echo "  ctags-clean   - Remove existing tags file"
	@echo "  ctags-watch   - Watch for file changes and auto-update ctags"
	@echo "  install       - Install project dependencies"
	@echo "  lint          - Run code linting"
	@echo "  test          - Run tests (if available)"
	@echo "  run           - Run the main application"
	@echo "  docs          - Generate documentation"

# Ctags targets
ctags:
	@echo "🏷️  Generating ctags..."
	@./update_ctags.sh

ctags-verbose:
	@echo "🏷️  Generating ctags (verbose)..."
	@./update_ctags.sh --verbose

ctags-clean:
	@echo "🗑️  Cleaning ctags..."
	@rm -f tags

ctags-watch:
	@echo "👀 Starting ctags watcher..."
	@./watch_ctags.sh

# Development targets
install:
	@echo "📦 Installing dependencies..."
	@cd desktop_analyzer && pip install -r requirements.txt

lint:
	@echo "🔍 Running linting..."
	@cd desktop_analyzer && python -m flake8 *.py || echo "Install flake8: pip install flake8"

test:
	@echo "🧪 Running tests..."
	@cd desktop_analyzer && python -m pytest . || echo "No tests found or pytest not installed"

run:
	@echo "🚀 Running application..."
	@cd desktop_analyzer && python main.py

docs:
	@echo "📚 Generating documentation..."
	@echo "Documentation available in docs/ directory"
	@ls -la docs/

# Show project statistics
stats:
	@echo "📊 Project Statistics:"
	@echo "Python files: $(shell find . -name '*.py' | wc -l)"
	@echo "Total lines of code: $(shell find . -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@if [ -f tags ]; then echo "Total tags: $(shell wc -l < tags)"; fi
	@echo "Directories: $(shell find . -type d | grep -v __pycache__ | grep -v .git | wc -l)"
