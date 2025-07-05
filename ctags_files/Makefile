# Makefile for ctags management
# Usage: make -f ctags_files/Makefile <target>

.PHONY: ctags clean validate help

# Default target
ctags:
	@echo "🏷️  Generating ctags for project..."
	@cd .. && ctags -R --fields=+iaS --extras=+q --output-format=e-ctags .
	@echo "✅ Tags generated successfully"

# Clean existing tags
clean:
	@echo "🗑️  Cleaning ctags files..."
	@rm -f ../tags ../tags.lock ../tags.temp
	@echo "✅ Cleaned"

# Validate ctags configuration and generated tags
validate:
	@echo "🔍 Validating ctags configuration..."
	@./validate_ctags.sh
	@echo "✅ Validation completed"

# Show help
help:
	@echo "Available targets:"
	@echo "  ctags    - Generate ctags for the project"
	@echo "  clean    - Remove existing tag files"
	@echo "  validate - Validate ctags configuration"
	@echo "  help     - Show this help message"
