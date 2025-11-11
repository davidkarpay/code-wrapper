# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a streaming AI coding assistant that connects to LM Studio for local LLM inference. It provides real-time streaming responses with visible "thinking" processes, making it ideal for proof-of-concept development and understanding how AI models reason through problems.

## Running the Agent

```bash
python coding_agent_streaming.py
```

## Architecture

### Core Design Pattern
The codebase implements a **streaming conversation agent** with real-time token visualization. The agent maintains conversation history and streams responses from a locally-hosted LM Studio server, displaying both the model's reasoning process ("thinking") and final responses.

### Key Components

**StreamingAgent Class** (`coding_agent_streaming.py`)
- Manages conversation history with system/user/assistant message roles
- Handles both streaming and non-streaming API requests to LM Studio
- Implements special "thinking" tag parsing to visualize model reasoning
- Provides token count statistics and performance metrics

**Configuration System**
- `agent_config.json`: Primary configuration for LM Studio connection, model settings, and agent behavior
- `system_prompt.txt`: Customizable system prompt loaded at agent initialization
- All settings can be modified at runtime via CLI commands

**Thinking Visualization**
The agent parses special `[THINKING]...[/THINKING]` and `[RESPONSE]...` tags in model outputs to separate reasoning from final answers. This allows users to see the model's step-by-step reasoning process before the actual response.

### LM Studio Integration

The agent connects to LM Studio's OpenAI-compatible API:
- Default endpoint: `http://localhost:1234/v1`
- Uses `/chat/completions` endpoint with streaming support
- Handles Server-Sent Events (SSE) for real-time token streaming
- Model: `qwen2.5-coder-1.5b-instruct` (configurable)

### Workspace Organization

The agent creates a working directory structure (auto-created as needed):
```
./agent_workspace/        # Primary working directory for agent operations
```

Additional workspace directories are defined in `agent_config.json` under `legal_workspace` (can be renamed/repurposed for any domain-specific organization).

## Configuration

### agent_config.json

**LM Studio Settings:**
- `url`: LM Studio API endpoint
- `model`: Model name loaded in LM Studio

**Agent Behavior:**
- `temperature`: 0.7 (controls randomness)
- `max_tokens`: 4096 (maximum response length)
- `stream`: true/false (enable real-time streaming)
- `show_token_count`: Display token statistics after responses
- `show_thinking`: Display model's reasoning process

**Workspace Directories:**
The `legal_workspace` section defines custom directory paths. These can be renamed and repurposed for any domain-specific file organization.

### system_prompt.txt

Defines the agent's role and behavior. The prompt can be customized for any domain or use case:
- Edit `system_prompt.txt` directly and restart the agent, OR
- Use the `/prompt` command during runtime to modify interactively

**Key Pattern:** The prompt should instruct the model to use `[THINKING]` tags for reasoning and `[RESPONSE]` tags for final answers. This enables the visualization of the model's step-by-step thought process.

**Current Default:** The included prompt is specialized for legal technology work but can be completely replaced for your POC development needs (e.g., web development, data science, system automation, etc.).

## Runtime Commands

Available during agent execution (prefix with `/`):
- `/stream` - Toggle streaming on/off
- `/thinking` - Toggle thinking display
- `/tokens` - Toggle token statistics
- `/prompt` - Edit system prompt (prompts for multi-line input, end with `END`)
- `/save_prompt` - Save current prompt to system_prompt.txt
- `/config` - Display current configuration
- `/reset` - Clear conversation history
- `/help` - Show command list
- `/exit` - Quit agent

## Important Context

**Local LLM Benefits:**
This agent uses LM Studio for fully local inference, providing:
- Complete control over the model and its responses
- No API costs or rate limits
- Ability to experiment freely during POC development
- Data stays on your laptop (useful for any privacy-sensitive work)

**Domain Customization:**
The included system prompt is specialized for legal work, but this is easily customizable:
- Modify `system_prompt.txt` for your specific domain (coding, data analysis, etc.)
- Use the `/prompt` command to experiment with different agent behaviors
- The `[THINKING]` tag pattern works for any domain - it helps visualize model reasoning during development

**Model Selection:**
The agent uses Qwen2.5-Coder by default (good for coding tasks), but any LM Studio-compatible model works:
- Update `model` field in `agent_config.json`
- Load the corresponding model in LM Studio
- Common alternatives: CodeLlama, DeepSeek-Coder, Mistral, etc.

**Streaming Visualization:**
When streaming is enabled, you see the model "think" in real-time:
- Thinking sections appear in dimmed text
- Responses display in normal text
- Token statistics show generation speed (useful for evaluating model performance)
- Great for debugging and understanding model behavior during POC development

**POC Development Workflow:**
This setup is ideal for prototyping AI-assisted workflows:
1. Experiment with different system prompts to tune agent behavior
2. Use thinking visualization to debug unexpected responses
3. Toggle streaming on/off to compare user experience
4. Monitor token statistics to optimize for performance
5. Test different models to find the best fit for your use case
