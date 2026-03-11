#!/bin/bash

# OpenClaw Layered Search Installation Script
# This script installs the skill and its dependencies including MediaCrawler

set -e

echo "=========================================="
echo "OpenClaw Layered Search Installation"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Install Python dependencies
echo "📦 Step 1/3: Installing Python dependencies..."
pip install -r requirements.txt

# Step 2: Install MediaCrawler
echo ""
echo "📦 Step 2/3: Installing MediaCrawler (for Chinese platform support)..."
MEDIACRAWLER_DIR="$SCRIPT_DIR/tools/MediaCrawler"

if [ -d "$MEDIACRAWLER_DIR" ]; then
    echo "   MediaCrawler already exists, updating..."
    cd "$MEDIACRAWLER_DIR"
    git pull
else
    echo "   Cloning MediaCrawler..."
    mkdir -p "$SCRIPT_DIR/tools"
    cd "$SCRIPT_DIR/tools"
    git clone https://github.com/NanmiCoder/MediaCrawler.git
    cd MediaCrawler
fi

# Install MediaCrawler dependencies
echo "   Installing MediaCrawler dependencies..."
if command -v uv &> /dev/null; then
    uv sync
    uv run playwright install chromium
else
    echo "   ⚠️  uv not found, using pip instead (slower)"
    pip install -r requirements.txt
    playwright install chromium
fi

cd "$SCRIPT_DIR"

# Step 3: Install Playwright browsers
echo ""
echo "📦 Step 3/3: Installing Playwright browsers..."
playwright install chromium

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "📚 Next steps:"
echo "   1. Test the installation: python3 test_integration.py"
echo "   2. Read QUICKSTART.md for usage instructions"
echo ""
echo "🎯 This skill uses MediaCrawler (https://github.com/NanmiCoder/MediaCrawler)"
echo "   for Chinese platform support. Thank you to the MediaCrawler team!"
echo ""
