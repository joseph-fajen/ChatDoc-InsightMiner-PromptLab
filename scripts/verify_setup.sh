#!/bin/bash
# Verify the setup of the ChatDoc-InsightMiner-PromptLab

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "Verifying ChatDoc-InsightMiner-PromptLab setup..."
echo "================================================="

# Check if Python is installed
echo -n "Checking Python installation... "
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}OK${NC} (${PYTHON_VERSION})"
else
    echo -e "${RED}FAILED${NC} - Python 3 is not installed or not in PATH"
    exit 1
fi

# Check Python version
echo -n "Checking Python version... "
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 9 ]; then
    echo -e "${GREEN}OK${NC} (Python ${PY_MAJOR}.${PY_MINOR})"
else
    echo -e "${YELLOW}WARNING${NC} - Python 3.9+ recommended, found ${PY_MAJOR}.${PY_MINOR}"
fi

# Check for required directories
echo -n "Checking required directories... "
MISSING_DIRS=""
for dir in "data" "docs" "prompts" "logs" "outputs" "vector_db"; do
    if [ ! -d "../$dir" ]; then
        MISSING_DIRS="$MISSING_DIRS $dir"
    fi
done

if [ -z "$MISSING_DIRS" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}WARNING${NC} - Missing directories:${MISSING_DIRS}"
    echo "Creating missing directories..."
    for dir in $MISSING_DIRS; do
        mkdir -p "../$dir"
        echo "Created ../$dir"
    done
fi

# Check for .env file
echo -n "Checking .env configuration... "
if [ -f "../.env" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}WARNING${NC} - .env file not found"
    if [ -f "../.env.example" ]; then
        echo "Creating .env from .env.example (you will need to update the API keys)"
        cp ../.env.example ../.env
    else
        echo -e "${RED}FAILED${NC} - Neither .env nor .env.example found"
    fi
fi

# Check for required packages
echo -n "Checking Python packages... "
MISSING_PKGS=""
REQUIRED_PKGS=("pandas" "python-dotenv" "tqdm" "chromadb" "sentence-transformers")

for pkg in "${REQUIRED_PKGS[@]}"; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        MISSING_PKGS="$MISSING_PKGS $pkg"
    fi
done

if [ -z "$MISSING_PKGS" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}WARNING${NC} - Missing Python packages:${MISSING_PKGS}"
    echo "You may need to run: pip install -r requirements.txt"
fi

# Check for sample data files
echo -n "Checking sample data files... "
if [ -f "../data/chat_data.csv" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}WARNING${NC} - No sample data found"
    echo "You will need to add chat data to the data directory."
fi

# Check for docs files
echo -n "Checking documentation files... "
DOC_COUNT=$(find ../docs -name "*.md" -o -name "*.mdx" | wc -l)
if [ "$DOC_COUNT" -gt 0 ]; then
    echo -e "${GREEN}OK${NC} (${DOC_COUNT} files found)"
else
    echo -e "${YELLOW}WARNING${NC} - No documentation files found"
    echo "You will need to add documentation files to the docs directory."
fi

# Summary
echo ""
echo "Setup verification completed!"
echo "-----------------------------"
echo "Next steps:"
echo "1. Ensure your .env file contains valid API keys"
echo "2. Build the vector database:"
echo "   python scripts/build_vector_db.py"
echo "3. Add documentation to the vector database:"
echo "   python scripts/add_docs_to_vector_db.py"
echo "4. Run your first analysis:"
echo "   python scripts/multi_llm_combined_analyzer.py --prompt prompts/analysis_prompts/technical_issues.txt"
echo ""