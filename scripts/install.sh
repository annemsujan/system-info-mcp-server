#!/bin/bash

# System Info MCP Server - Auto Installer
# Detects user preference and installs accordingly

echo "🚀 System Info MCP Server Installer"
echo "===================================="

# Check if Node.js is available
if command -v node &> /dev/null && command -v npx &> /dev/null; then
    NODE_AVAILABLE=true
    NODE_VERSION=$(node --version)
    echo "✅ Node.js detected: $NODE_VERSION"
else
    NODE_AVAILABLE=false
    echo "❌ Node.js not detected"
fi

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_AVAILABLE=true
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python detected: $PYTHON_VERSION"
    
    # Check if pipx is available
    if command -v pipx &> /dev/null; then
        PIPX_AVAILABLE=true
        echo "✅ pipx detected"
    else
        PIPX_AVAILABLE=false
        echo "⚠️  pipx not detected (can be installed)"
    fi
else
    PYTHON_AVAILABLE=false
    PIPX_AVAILABLE=false
    echo "❌ Python not detected"
fi

echo ""

# Recommend best option
if [ "$NODE_AVAILABLE" = true ]; then
    echo "🎯 Recommended: Node.js implementation (fastest setup)"
    echo "   Command: npx @system-info/mcp-server@latest --test"
    echo ""
fi

if [ "$PYTHON_AVAILABLE" = true ] && [ "$PIPX_AVAILABLE" = true ]; then
    echo "🐍 Alternative: Python implementation with pipx"
    echo "   Command: pipx run system-info-mcp-server --test"
    echo ""
fi

# Interactive selection
echo "Choose installation method:"
if [ "$NODE_AVAILABLE" = true ]; then
    echo "1) Node.js with npx (recommended)"
fi
if [ "$PYTHON_AVAILABLE" = true ]; then
    echo "2) Python with pipx"
    echo "3) Python with pip"
fi
echo "4) Show manual installation instructions"
echo "5) Exit"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        if [ "$NODE_AVAILABLE" = true ]; then
            echo "🚀 Testing Node.js implementation..."
            npm install
            npm test
            echo ""
            echo "✅ Success! Add this to your Claude Desktop config:"
            echo '{
  "mcpServers": {
    "system-info": {
      "command": "node",
      "args": ["'$(pwd)'/dist/index.js"]
    }
  }
}'
        else
            echo "❌ Node.js not available. Please install Node.js first."
        fi
        ;;
    2)
        if [ "$PYTHON_AVAILABLE" = true ]; then
            if [ "$PIPX_AVAILABLE" = false ]; then
                echo "📦 Installing pipx..."
                pip3 install pipx
                echo "🔄 Updating PATH..."
                pipx ensurepath
                echo "⚠️  Please restart your terminal and run this script again."
                exit 0
            fi
            echo "🚀 Testing Python implementation with pipx..."
            cd python
            pip install -e .
            python -m system_info_mcp.server --test
            echo ""
            echo "✅ Success! Add this to your Claude Desktop config:"
            echo '{
  "mcpServers": {
    "system-info": {
      "command": "python",
      "args": ["-m", "system_info_mcp.server"],
      "cwd": "'$(pwd)'"
    }
  }
}'
        else
            echo "❌ Python not available. Please install Python first."
        fi
        ;;
    3)
        if [ "$PYTHON_AVAILABLE" = true ]; then
            echo "🚀 Installing Python implementation with pip..."
            cd python
            pip3 install -e .
            echo "🧪 Testing installation..."
            python -m system_info_mcp.server --test
            echo ""
            echo "✅ Success! Add this to your Claude Desktop config:"
            echo '{
  "mcpServers": {
    "system-info": {
      "command": "python",
      "args": ["-m", "system_info_mcp.server"],
      "cwd": "'$(pwd)'"
    }
  }
}'
        else
            echo "❌ Python not available. Please install Python first."
        fi
        ;;
    4)
        echo "📖 Manual Installation Instructions"
        echo "=================================="
        echo ""
        echo "Node.js Implementation:"
        echo "  1. Install Node.js from https://nodejs.org"
        echo "  2. Run: npm install && npm test"
        echo "  3. Add to Claude config with local path"
        echo ""
        echo "Python Implementation:"
        echo "  1. Install Python 3.8+ from https://python.org"
        echo "  2. cd python && pip install -e ."
        echo "  3. Test: python -m system_info_mcp.server --test"
        echo "  4. Add to Claude config with local path"
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📁 Claude Desktop config file locations:"
echo "  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "  Windows: %APPDATA%\Claude\claude_desktop_config.json"
echo "  Linux: ~/.config/Claude/claude_desktop_config.json"
echo ""
echo "🎉 Installation complete! Restart Claude Desktop to use the new server."