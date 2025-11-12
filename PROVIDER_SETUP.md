# Provider Setup Guide

This Python agent now supports multiple LLM providers with OpenAI-compatible APIs.

## Supported Providers

- **LM Studio** - Local LLM inference
- **Ollama** - Local and cloud LLM inference

## Configuration

### Switching Providers

Edit your config file (`agent_config_streaming.json` or `agent_config_streaming_v1.1.json`) and change the `provider` field:

```json
{
  "provider": "lm_studio"   // or "ollama"
}
```

### LM Studio Setup

1. Install and run LM Studio
2. Load your desired model
3. Enable the local server (default: `http://localhost:1234`)
4. Update the config:

```json
{
  "provider": "lm_studio",
  "lm_studio": {
    "url": "http://127.0.0.1:1234/v1",
    "model": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
    "api_key": null
  }
}
```

### Ollama Local Setup

1. Install Ollama
2. Pull your desired model: `ollama pull model-name`
3. Ollama server runs automatically at `http://localhost:11434`
4. Update the config:

```json
{
  "provider": "ollama",
  "ollama": {
    "url": "http://localhost:11434/v1",
    "model": "gemma3",
    "api_key": null
  }
}
```

### Ollama Cloud Setup

1. Get your API key from ollama.com
2. Update the config:

```json
{
  "provider": "ollama",
  "ollama": {
    "url": "https://ollama.com/v1",
    "model": "gpt-oss:120b-cloud",
    "api_key": "YOUR_API_KEY_HERE"
  }
}
```

**IMPORTANT:** Replace `YOUR_API_KEY_HERE` with your actual API key.

## API Key Security

**Never commit your API key to version control!**

Options for keeping your API key secure:

1. **Use environment variables:**
   - Set: `export OLLAMA_API_KEY="your-key-here"`
   - Modify the code to read from environment

2. **Use a separate untracked config:**
   - Create `agent_config.local.json`
   - Add to `.gitignore`
   - Load this config instead

3. **Use a secrets file:**
   - Create `.secrets.json` with just your API keys
   - Add to `.gitignore`
   - Load and merge with main config

## Verifying Your Setup

Run the agent and use the `/config` command to verify your settings:

```
python coding_agent_streaming.py
```

Then type `/config` to see:
- Provider name
- API URL
- Model name
- Whether API key is set

## Troubleshooting

**Connection errors:**
- LM Studio: Make sure the server is enabled and running
- Ollama local: Run `ollama serve` if not auto-started
- Ollama cloud: Verify your API key and internet connection

**Model not found:**
- LM Studio: Load the model in the UI first
- Ollama: Pull the model with `ollama pull model-name`

**Authentication errors:**
- Double-check your API key
- Make sure there are no extra spaces
- Verify the key is valid on ollama.com
