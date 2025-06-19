#!/bin/bash

# Test both implementations of System Info MCP Server

echo "🧪 Testing Both System Info MCP Server Implementations"
echo "======================================================"

# Test Node.js implementation
echo "📊 Testing Node.js Implementation..."
echo "-----------------------------------"
if command -v node &> /dev/null; then
    if [ -f "package.json" ]; then
        npm install --silent
        npm test
        NODE_EXIT_CODE=$?
        if [ $NODE_EXIT_CODE -eq 0 ]; then
            echo "✅ Node.js implementation: PASSED"
        else
            echo "❌ Node.js implementation: FAILED"
        fi
    else
        echo "⚠️  package.json not found - skipping Node.js test"
        NODE_EXIT_CODE=1
    fi
else
    echo "⚠️  Node.js not available - skipping Node.js test"
    NODE_EXIT_CODE=1
fi

echo ""

# Test Python implementation
echo "🐍 Testing Python Implementation..."
echo "----------------------------------"
if command -v python3 &> /dev/null; then
    if [ -d "python" ]; then
        cd python
        pip install -e . --quiet
        python -m system_info_mcp.server --test
        PYTHON_EXIT_CODE=$?
        cd ..
        if [ $PYTHON_EXIT_CODE -eq 0 ]; then
            echo "✅ Python implementation: PASSED"
        else
            echo "❌ Python implementation: FAILED"
        fi
    else
        echo "⚠️  python/ directory not found - skipping Python test"
        PYTHON_EXIT_CODE=1
    fi
else
    echo "⚠️  Python not available - skipping Python test"
    PYTHON_EXIT_CODE=1
fi

echo ""
echo "📋 Test Summary"
echo "==============="

if [ $NODE_EXIT_CODE -eq 0 ]; then
    echo "✅ Node.js: Working"
else
    echo "❌ Node.js: Failed or not available"
fi

if [ $PYTHON_EXIT_CODE -eq 0 ]; then
    echo "✅ Python: Working"
else
    echo "❌ Python: Failed or not available"
fi

# Overall result
if [ $NODE_EXIT_CODE -eq 0 ] || [ $PYTHON_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 At least one implementation is working!"
    echo "You can use either in Claude Desktop."
    exit 0
else
    echo ""
    echo "⚠️  Both implementations failed. Please check your environment."
    exit 1
fi