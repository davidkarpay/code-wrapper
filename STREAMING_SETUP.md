# Streaming AI Coding Agent Setup Guide

## Features Added
✅ **Real-time token streaming** - See each word as it's generated
✅ **Thinking visualization** - Watch the model reason through problems
✅ **Token statistics** - Tokens per second, total count, generation time
✅ **Customizable prompts** - Edit system prompt on the fly
✅ **Toggle controls** - Turn features on/off during conversation  

## Files to Download

1. **[coding_agent_streaming.py](coding_agent_streaming.py)** - Main streaming agent
2. **[agent_config_streaming.json](agent_config_streaming.json)** - Configuration file
3. **[system_prompt.txt](system_prompt.txt)** - Customizable system prompt

Save all files to your preferred directory

## LM Studio Settings

For best streaming performance, adjust these settings in LM Studio:

### Server Settings Tab
- ☑️ **Server Port**: 1234 (default)
- ☐ **Serve on Local Network**: OFF (use localhost)
- ☑️ **Allow per-request remote MCPs**: ON
- ☐ **Enable CORS**: OFF (not needed for local)
- ☑️ **Just-in-Time Model Loading**: ON
- ☑️ **Auto unload unused JIT loaded models**: ON (60 minutes)
- ☑️ **Only Keep Last JIT Loaded Model**: ON

### Model Settings (when Qwen is loaded)
- **Temperature**: 0.7 (or adjust in agent)
- **Max Tokens**: 4096
- **Context Length**: 32768 (if supported)
- **GPU Layers**: Maximum your GPU can handle
- **CPU Threads**: 4-8 (based on your CPU)

### Inference Settings
- **Prompt Format**: ChatML (for Qwen)
- **Stream**: Will be controlled by agent
- **Batch Size**: 512
- **Threads**: 4-8

## Running the Streaming Agent

```bash
cd /path/to/your/directory

# Run the streaming agent
python coding_agent_streaming.py
```

## New Commands Available

While chatting with the agent, use these commands:

- `/stream` - Toggle streaming on/off
- `/thinking` - Toggle thinking display on/off  
- `/tokens` - Toggle token statistics on/off
- `/prompt` - Edit the system prompt
- `/save_prompt` - Save current prompt to file
- `/config` - Show all settings
- `/reset` - Clear conversation history
- `/help` - Show all commands
- `/exit` - Quit

## How It Works

### 1. Streaming Mode (Default: ON)
```
You: How do I build a REST API with FastAPI?

Agent: [Generating...]
[THINKING]
1. User wants to create a REST API using FastAPI
2. Should cover basic setup, routing, and best practices
3. Include a complete working example
[/THINKING]

[RESPONSE]
To build a REST API with FastAPI, start by installing... [text appears word by word]

[156 tokens | 2.3s | 67.8 tok/s]
```

### 2. Thinking Display (Default: ON)
The model shows its reasoning process before answering complex technical questions.

### 3. Token Statistics (Default: ON)
After each response, see:
- Total tokens generated
- Time taken
- Tokens per second

## Customizing the System Prompt

### Method 1: Edit During Chat
```
You: /prompt
[Shows current prompt]
Enter new prompt (type END on a new line when done):
You are an expert in web development focusing on React and Node.js...
[your custom prompt]
END
✓ System prompt updated and conversation reset.
```

### Method 2: Edit File Directly
Edit `system_prompt.txt` and restart the agent.

## Example Domain-Specific Prompts

### Web Development Focus
```
You are an expert full-stack web developer specializing in modern frameworks.
Focus on React, Next.js, Node.js, and TypeScript.
Provide complete, working code examples with best practices.
Include error handling and explain architectural decisions.
Suggest testing strategies and deployment options.
```

### Data Science Focus
```
You are a data science and machine learning expert.
Specialize in Python, pandas, scikit-learn, and visualization.
Provide clean, reproducible code with clear explanations.
Include data validation and error handling.
Suggest alternative approaches and optimization strategies.
```

### DevOps/Infrastructure Focus
```
You are a DevOps and infrastructure automation specialist.
Focus on Docker, Kubernetes, CI/CD, and infrastructure as code.
Provide practical, production-ready configurations.
Explain trade-offs and security considerations.
Suggest monitoring and scaling strategies.
```

## Troubleshooting

### "Connection refused"
- Ensure LM Studio is running
- Check server is started (green "Running" status)
- Verify URL is `http://localhost:1234/v1`

### Slow streaming
- Reduce max_tokens in config
- Increase GPU layers in LM Studio
- Close other applications

### No thinking shown
- Check `/thinking` command to enable
- Ensure prompt includes thinking instructions
- Some simple queries won't trigger thinking

### Tokens not displaying
- Use `/tokens` command to enable
- Check terminal supports ANSI colors

## Performance Tips

1. **GPU Acceleration**: Maximize GPU layers in LM Studio for faster generation
2. **Context Management**: Use `/reset` periodically to clear long conversations
3. **Temperature**: Lower (0.3-0.5) for factual/code, higher (0.7-0.9) for creative
4. **Batch Processing**: For multiple similar tasks, keep context with examples

## Next Steps

1. Test with simple query: "Hi, what can you do?"
2. Try complex query to see thinking: "Build a REST API with authentication"
3. Customize prompt for your specific domain
4. Experiment with temperature settings
5. Add your own specialized prompts for your use case

The streaming agent provides excellent visibility into the model's generation process and thinking, making it ideal for POC development and understanding how the AI reasons through complex technical problems.
