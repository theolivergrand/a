#!/bin/bash

# Script to generate and update ctags for the project
# Usage: ./ctags_files/update_ctags.sh [--verbose]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🏷️  Updating ctags for Desktop UI/UX Analyzer project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if ctags is installed
if ! command -v ctags &> /dev/null; then
    echo -e "${RED}❌ ctags is not installed${NC}"
    echo -e "${YELLOW}💡 Install with: sudo apt-get install universal-ctags${NC}"
    exit 1
fi

# Check ctags version
CTAGS_VERSION=$(ctags --version | head -n1)
echo -e "${BLUE}📋 Using: $CTAGS_VERSION${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Remove old tags file if it exists
if [ -f "tags" ]; then
    echo -e "${YELLOW}🗑️  Removing old tags file...${NC}"
    rm -f tags
fi

# Generate ctags
echo -e "${BLUE}🔍 Scanning project files...${NC}"

if [ "$1" = "--verbose" ] || [ "$1" = "-v" ]; then
    echo -e "${BLUE}📝 Generating tags with verbose output...${NC}"
    ctags -R \
        --verbose \
        --fields=+iaS \
        --extras=+q \
        --output-format=e-ctags \
        .
else
    echo -e "${BLUE}📝 Generating tags...${NC}"
    ctags -R \
        --fields=+iaS \
        --extras=+q \
        --output-format=e-ctags \
        . 2>/dev/null || {
        echo -e "${RED}❌ Failed to generate tags${NC}"
        exit 1
    }
fi

# Check if tags file was created successfully
if [ -f "tags" ]; then
    TAG_COUNT=$(wc -l < tags)
    echo -e "${GREEN}✅ Tags file generated successfully!${NC}"
    echo -e "${GREEN}📊 Total tags: $TAG_COUNT${NC}"
    
    # Show some statistics
    echo -e "\n${BLUE}📈 Tag Statistics:${NC}"
    echo -e "  Functions: $(grep -c '\tf\t' tags 2>/dev/null || echo 0)"
    echo -e "  Classes:   $(grep -c '\tc\t' tags 2>/dev/null || echo 0)"
    echo -e "  Methods:   $(grep -c '\tm\t' tags 2>/dev/null || echo 0)"
    echo -e "  Variables: $(grep -c '\tv\t' tags 2>/dev/null || echo 0)"
    echo -e "  Constants: $(grep -c '\tC\t' tags 2>/dev/null || echo 0)"
    echo -e "  Widgets:   $(grep -c '\tw\t' tags 2>/dev/null || echo 0)"
    echo -e "  Signals:   $(grep -c '\ts\t' tags 2>/dev/null || echo 0)"
    
    # Show recent tags (last 10)
    echo -e "\n${BLUE}🏷️  Recent tags:${NC}"
    tail -n 10 tags | while read -r line; do
        tag_name=$(echo "$line" | cut -f1)
        tag_type=$(echo "$line" | cut -f4 | cut -c1)
        echo -e "  ${YELLOW}$tag_name${NC} ($tag_type)"
    done
    
    echo -e "\n${GREEN}🎉 Ctags update completed successfully!${NC}"
else
    echo -e "${RED}❌ Failed to generate tags file${NC}"
    exit 1
fi

# Optional: Update .gitignore to exclude tags file
if ! grep -q "^tags$" .gitignore 2>/dev/null; then
    echo -e "\n${YELLOW}💡 Consider adding 'tags' to .gitignore to exclude it from version control${NC}"
fi

echo -e "\n${BLUE}💡 Usage tips:${NC}"
echo -e "  • Use Ctrl+] to jump to definition"
echo -e "  • Use Ctrl+T to jump back"
echo -e "  • Run './update_ctags.sh --verbose' for detailed output"
echo -e "  • Use 'tags' command in vim/nvim for tag navigation"
