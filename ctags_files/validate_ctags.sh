#!/bin/bash

# Ctags configuration validation script
# Checks that ctags is properly configured and working

set -e

echo "🔍 Validating ctags configuration..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0

# Check if ctags is installed
if ! command -v ctags &> /dev/null; then
    echo -e "${RED}❌ ctags is not installed${NC}"
    echo -e "${YELLOW}💡 Install with: sudo apt-get install universal-ctags${NC}"
    exit 1
else
    echo -e "${GREEN}✅ ctags is installed${NC}"
fi

# Check ctags version
CTAGS_VERSION=$(ctags --version | head -n1)
echo -e "${BLUE}📋 Version: $CTAGS_VERSION${NC}"

# Check configuration files
echo -e "\n${BLUE}📁 Configuration files:${NC}"
if [ -d ".ctags.d" ]; then
    echo -e "${GREEN}✅ .ctags.d directory exists${NC}"
    for config_file in .ctags.d/*.ctags; do
        if [ -f "$config_file" ]; then
            echo -e "  ${GREEN}✅ $config_file${NC}"
        fi
    done
else
    echo -e "${RED}❌ .ctags.d directory not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test configuration syntax
echo -e "\n${BLUE}⚙️  Testing configuration syntax:${NC}"
if ctags --list-kinds=Python &> /dev/null; then
    echo -e "${GREEN}✅ Configuration syntax is valid${NC}"
else
    echo -e "${RED}❌ Configuration syntax errors detected${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test tag generation
echo -e "\n${BLUE}🏷️  Testing tag generation:${NC}"
TEST_FILE="/tmp/test_ctags.py"
cat > "$TEST_FILE" << 'EOF'
class TestClass:
    def __init__(self):
        self.widget = QPushButton()
        self.signal = pyqtSignal()
    
    def test_method(self):
        pass

def test_function():
    pass

CONSTANT_VALUE = "test"
EOF

# Generate tags for test file
if ctags --fields=+iaS --extras=+q "$TEST_FILE" -o /tmp/test_tags 2>/dev/null; then
    echo -e "${GREEN}✅ Tag generation successful${NC}"
    
    # Check for expected tag types
    if grep -q "\tc\t" /tmp/test_tags; then
        echo -e "  ${GREEN}✅ Class detection working${NC}"
    else
        echo -e "  ${RED}❌ Class detection failed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    if grep -q "\tm\t" /tmp/test_tags; then
        echo -e "  ${GREEN}✅ Method detection working${NC}"
    else
        echo -e "  ${RED}❌ Method detection failed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    if grep -q "\tf\t" /tmp/test_tags; then
        echo -e "  ${GREEN}✅ Function detection working${NC}"
    else
        echo -e "  ${RED}❌ Function detection failed${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Check custom types (these might not work with basic test)
    if grep -q "\tw\t" /tmp/test_tags; then
        echo -e "  ${GREEN}✅ Widget detection working${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Widget detection not found (expected for test file)${NC}"
    fi
    
    if grep -q "\ts\t" /tmp/test_tags; then
        echo -e "  ${GREEN}✅ Signal detection working${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Signal detection not found (expected for test file)${NC}"
    fi
    
    if grep -q "\tC\t" /tmp/test_tags; then
        echo -e "  ${GREEN}✅ Constant detection working${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Constant detection not found (expected for test file)${NC}"
    fi
    
else
    echo -e "${RED}❌ Tag generation failed${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Clean up test files
rm -f "$TEST_FILE" /tmp/test_tags

# Check project-specific functionality
echo -e "\n${BLUE}🎯 Project-specific checks:${NC}"
if [ -f "tags" ]; then
    TAG_COUNT=$(wc -l < tags)
    echo -e "${GREEN}✅ Project tags file exists ($TAG_COUNT tags)${NC}"
    
    # Check for expected project classes
    if grep -q "BoundingBox" tags; then
        echo -e "  ${GREEN}✅ BoundingBox class found${NC}"
    else
        echo -e "  ${YELLOW}⚠️  BoundingBox class not found${NC}"
    fi
    
    if grep -q "ImageCanvas" tags; then
        echo -e "  ${GREEN}✅ ImageCanvas class found${NC}"
    else
        echo -e "  ${YELLOW}⚠️  ImageCanvas class not found${NC}"
    fi
    
    if grep -q "MainWindow" tags; then
        echo -e "  ${GREEN}✅ MainWindow class found${NC}"
    else
        echo -e "  ${YELLOW}⚠️  MainWindow class not found${NC}"
    fi
    
else
    echo -e "${YELLOW}⚠️  Project tags file not found. Run './update_ctags.sh' first.${NC}"
fi

# Check scripts
echo -e "\n${BLUE}📜 Script validation:${NC}"
for script in update_ctags.sh watch_ctags.sh; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo -e "  ${GREEN}✅ $script is executable${NC}"
    elif [ -f "$script" ]; then
        echo -e "  ${YELLOW}⚠️  $script exists but not executable${NC}"
    else
        echo -e "  ${RED}❌ $script not found${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Final report
echo -e "\n${BLUE}📊 Validation Summary:${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Ctags is properly configured.${NC}"
    echo -e "\n${BLUE}💡 Usage reminders:${NC}"
    echo -e "  • Run './update_ctags.sh' to generate/update tags"
    echo -e "  • Use 'make ctags' for convenience"
    echo -e "  • Use Ctrl+] in vim to jump to definitions"
    echo -e "  • Install a ctags extension in VS Code for navigation"
else
    echo -e "${RED}❌ $ERRORS error(s) found. Please fix the issues above.${NC}"
    exit 1
fi
