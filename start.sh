#!/bin/bash

# NIST Statistical Tests - Startup Script
# Automatically checks installation and starts the application

echo "=================================================="
echo "NIST Statistical Tests Application"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Dependencies not found. Installing..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Verify installation
echo "Verifying installation..."
python3 verify_installation.py --quiet 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Installation verified"
else
    echo "⚠️  Some checks failed, but attempting to start anyway..."
fi
echo ""

# Start the application
echo "=================================================="
echo "Starting Streamlit application..."
echo "=================================================="
echo ""
echo "The application will open in your browser at:"
echo "  → http://localhost:8501"
echo ""
echo "To stop the application, press Ctrl+C"
echo ""

# Add streamlit to PATH if needed
if ! command -v streamlit &> /dev/null; then
    export PATH="$HOME/Library/Python/3.9/bin:$PATH"
fi

# Start streamlit
streamlit run app.py

# If streamlit command not found, try with python module
if [ $? -ne 0 ]; then
    python3 -m streamlit run app.py
fi

