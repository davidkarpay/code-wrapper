#!/bin/bash
# Quick start script for Multi-Agent AI Coding System

echo "🤖 Multi-Agent AI Coding System"
echo "================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if required dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  aiohttp not found. Installing dependencies..."
    pip3 install -r requirements_multi_agent.txt
else
    echo "✅ Dependencies OK"
fi

# Check if config file exists
if [ ! -f "agent_config_multi_agent.json" ]; then
    echo "❌ Configuration file not found: agent_config_multi_agent.json"
    exit 1
fi

# Check if secrets file exists
if [ ! -f "secrets.json" ]; then
    echo "⚠️  secrets.json not found"
    echo "📝 Creating secrets.json template..."
    echo '{
  "ollama_api_key": "YOUR_OLLAMA_API_KEY_HERE",
  "lm_studio_api_key": null
}' > secrets.json
    echo "✅ Created secrets.json - Please add your API keys"
    echo ""
    read -p "Press Enter to continue after adding your API keys..."
fi

# Create prompts directory if it doesn't exist
mkdir -p prompts

echo ""
echo "🚀 Starting Multi-Agent System..."
echo ""

# Run the orchestrator
python3 multi_agent_orchestrator.py

echo ""
echo "👋 Goodbye!"
