#!/bin/bash

# Poker Chip Distribution - Startup Script
# This script starts the FastAPI server with the web UI

echo "🎰 Poker Chip Distribution Calculator"
echo "======================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo ""
    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Start the server
echo ""
echo "🚀 Starting server..."
echo ""
echo "======================================"
echo "Access the application at:"
echo "  Web UI:      http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  Health:      http://localhost:8000/health"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the API
python3 api.py
