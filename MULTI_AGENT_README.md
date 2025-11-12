# Multi-Agent AI Coding System

A concurrent multi-agent orchestration system that enables a main AI agent to spawn and coordinate specialized sub-agents using different model sizes for cost optimization and parallel task execution.

## Overview

This system extends the single-agent coding assistant with:
- **Main Agent** (e.g., gpt-oss:120b-cloud) - Primary orchestration and decision-making
- **Sub-Agents** (e.g., gpt-oss:20b-cloud) - Specialized tasks like code review, research, testing
- **Concurrent Execution** - Multiple agents work in parallel
- **Isolated Contexts** - Each agent maintains separate conversation history
- **Summarization** - Sub-agents send summaries back to main agent
- **Cost Optimization** - Use smaller models for simpler tasks

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  MultiAgentOrchestrator                 │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │AgentManager  │  │OutputManager │  │ AsyncAgent   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │  Main   │      │Reviewer │      │Research │
   │  Agent  │      │  Agent  │      │  Agent  │
   │ (120b)  │      │  (20b)  │      │  (20b)  │
   └─────────┘      └─────────┘      └─────────┘
```

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements_multi_agent.txt
   ```

2. **Configure API Keys**

   Create `secrets.json` in the project root:
   ```json
   {
     "ollama_api_key": "your-ollama-api-key-here",
     "lm_studio_api_key": null
   }
   ```

3. **Configure Agents**

   Edit `agent_config_multi_agent.json` to customize:
   - Model selections for each agent role
   - Temperature and token limits
   - System prompts for each role
   - Spawning rules and keywords

## Running the System

### Basic Usage

```bash
python multi_agent_orchestrator.py
```

### Commands

#### Agent Management
- `/spawn <role> <task>` - Spawn a specialized sub-agent
  ```
  /spawn reviewer Review the authentication module for security issues
  /spawn researcher Find best practices for async Python database connections
  /spawn implementer Implement JWT token validation
  /spawn tester Test the user registration flow
  /spawn optimizer Analyze performance of the data processing pipeline
  ```

- `/agents` - List all active agents and their status
- `/stop <agent_id>` - Terminate a specific sub-agent
- `/stop_all` - Terminate all sub-agents

#### Communication
- Regular message → Main agent
- `@<agent_id> message` → Direct message to specific agent

#### Configuration
- `/config` - Show current configuration
- `/stats` - Show agent statistics and message counts
- `/stream` - Toggle streaming mode (main agent)
- `/thinking` - Toggle thinking display (main agent)

#### Session
- `/reset` - Reset main agent conversation
- `/help` - Show all commands
- `/exit` - Exit the system

## Example Workflows

### 1. Code Review Workflow

```
You: I need to implement user authentication. Let's plan this out.

[Main agent responds with plan]

You: /spawn reviewer Review the authentication approach for security concerns

[Reviewer agent analyzes and provides security review]

[Main agent receives summary and incorporates feedback]

You: /spawn implementer Implement the authentication module based on the review

[Implementer creates the code]

You: /spawn tester Test the authentication implementation

[Tester validates the code]
```

### 2. Research and Implementation

```
You: /spawn researcher Research best Python async database libraries for PostgreSQL

[Researcher agent gathers information]

You: Based on the research, implement database connection pooling

[Main agent implements using research findings]

You: /spawn optimizer Review the database code for performance improvements

[Optimizer suggests optimizations]
```

### 3. Parallel Task Execution

```
You: /spawn reviewer Review module A
You: /spawn tester Test module B
You: /spawn researcher Research deployment options

[All three agents work concurrently]

[Main agent receives all summaries and coordinates next steps]
```

## Agent Roles

### Main Agent (120b model)
- **Purpose**: Orchestration, complex reasoning, decision-making
- **Temperature**: 0.7
- **Use**: Primary conversation, architecture decisions

### Reviewer Agent (20b model)
- **Purpose**: Code review, security analysis, quality checks
- **Temperature**: 0.3 (precise, analytical)
- **Outputs**: Review status, issues found, recommendations

### Researcher Agent (20b model)
- **Purpose**: Information gathering, fact-checking, documentation research
- **Temperature**: 0.5 (balanced)
- **Outputs**: Key findings, recommendations, confidence level

### Implementer Agent (20b model)
- **Purpose**: Writing code, implementing features
- **Temperature**: 0.6 (creative but focused)
- **Outputs**: Files modified, features added, testing notes

### Tester Agent (20b model)
- **Purpose**: Testing, validation, bug finding
- **Temperature**: 0.4 (systematic)
- **Outputs**: Test status, failures, recommendations

### Optimizer Agent (20b model)
- **Purpose**: Performance optimization, efficiency improvements
- **Temperature**: 0.5 (balanced)
- **Outputs**: Optimizations suggested, expected impact, trade-offs

## Configuration

### Agent Profiles

Each agent profile in `agent_config_multi_agent.json` defines:

```json
{
  "provider": "ollama",           // "ollama" or "lm_studio"
  "url": "https://ollama.com/v1", // API endpoint
  "model": "gpt-oss:20b-cloud",   // Model to use
  "api_key": "YOUR_KEY",          // API key (or from secrets.json)
  "role": "reviewer",             // Agent role
  "temperature": 0.3,             // Randomness (0-1)
  "max_tokens": 2048,             // Max response length
  "stream": true,                 // Enable streaming
  "system_prompt_file": "prompts/reviewer_prompt.txt"
}
```

### Automatic Spawning

Enable automatic sub-agent spawning based on keywords:

```json
{
  "spawning_rules": {
    "keywords": {
      "review": "reviewer_agent",
      "test": "tester_agent",
      "research": "researcher_agent",
      "optimize": "optimizer_agent"
    },
    "auto_spawn_on_keywords": true,
    "require_confirmation": false
  }
}
```

## Summary Format

Sub-agents MUST provide summaries using `[SUMMARY]` tags:

```
[SUMMARY]
Status: PASS/FAIL
Key Points:
- Point 1
- Point 2
Recommendation: Action to take
[/SUMMARY]
```

This ensures the main agent gets concise, actionable information without context pollution.

## Technical Details

### Async Architecture
- Uses `aiohttp` for concurrent API requests
- Non-blocking I/O for parallel agent execution
- Asyncio event loop for coordination

### Thread Safety
- File operations use reentrant locks (`threading.RLock`)
- Prevents concurrent write conflicts
- Safe for parallel agent file access

### Output Management
- Multiplexed display with visual separation
- Color-coded agent outputs
- Role-specific emoji indicators
- Prevents output collision

### Context Isolation
- Each agent has separate conversation history
- Sub-agents receive full main conversation on spawn
- Summaries prevent context bleeding back to main

## Cost Optimization

Using different model sizes provides significant cost savings:

| Scenario | Single 120b | Multi-Agent (120b + 20b) | Savings |
|----------|-------------|--------------------------|---------|
| Simple review task | 1x 120b | 1x 20b | ~83% |
| Research + implement | 2x 120b | 1x 120b + 1x 20b | ~42% |
| Parallel tasks (3) | 3x 120b | 1x 120b + 2x 20b | ~56% |

*Assumes 120b is 6x cost of 20b*

## Troubleshooting

### Agent Won't Spawn
- Check API key in `secrets.json`
- Verify profile exists in config
- Check max_concurrent_agents limit

### No Summary from Sub-Agent
- Ensure system prompt includes `[SUMMARY]` instructions
- Check that sub-agent completed successfully
- Verify agent terminated properly

### Output Collision
- System uses locks to prevent this
- If issues occur, check OutputManager settings
- Reduce max_concurrent_agents if needed

## Files

### Core System
- `multi_agent_orchestrator.py` - Main entry point
- `agent_manager.py` - Agent lifecycle management
- `output_manager.py` - Multiplexed output handling
- `async_streaming_agent.py` - Async agent implementation

### Configuration
- `agent_config_multi_agent.json` - Multi-agent config
- `secrets.json` - API keys (create this)
- `prompts/*.txt` - Role-specific system prompts

### Original System (Still Works)
- `coding_agent_streaming.py` - Original single-agent system
- `agent_config.json` - Original configuration

## Extending the System

### Add a New Agent Role

1. Add profile to `agent_config_multi_agent.json`
2. Create system prompt in `prompts/your_role_prompt.txt`
3. Add role to `AgentRole` enum in `agent_manager.py`
4. Add color/emoji mappings in `output_manager.py`
5. Spawn with `/spawn your_role Task description`

### Custom Model Configuration

Add any OpenAI-compatible API:

```json
{
  "custom_agent": {
    "provider": "ollama",
    "url": "https://your-api.com/v1",
    "model": "your-model-name",
    "api_key": "your-key",
    // ... rest of config
  }
}
```

## Phase 2: Workflow Engine ✅ COMPLETE

**Status:** ✅ Released (100% test pass rate - 23/23 tests)

The multi-agent system now includes a workflow engine for automated multi-step task execution with approval workflows and rollback capabilities.

### What's New in Phase 2

#### Workflow Plans

Agents can now propose structured multi-step plans:

```
[PLAN]
## Workflow: Implement and Test Feature

### Step 1: Research best practices
- Agent: researcher
- Tool: execute_bash
- Arguments: {"command": "grep -r 'pattern' ./docs"}
- Dependencies: none
- Estimated Time: 30s

### Step 2: Implement feature
- Agent: implementer
- Tool: write_file_tool
- Arguments: {"path": "./feature.py", "content": "..."}
- Dependencies: Step 1
- Estimated Time: 120s

### Step 3: Test implementation
- Agent: tester
- Tool: execute_bash
- Arguments: {"command": "pytest ./tests/test_feature.py"}
- Dependencies: Step 2
- Estimated Time: 45s

## Total Estimated Time: 195s (3m 15s)
## Cost Estimate: $0.06
[/PLAN]
```

#### Plan Approval Workflow

When an agent proposes a plan:
1. Plan is automatically detected and parsed
2. User sees formatted plan with steps, costs, and dependencies
3. User can Approve, Reject, Modify, or View details
4. Approved plans execute with real-time progress tracking
5. Failed plans trigger automatic rollback

#### Workflow Commands

```bash
/plans                  # List pending workflow plans
/approve <plan_id>      # Execute an approved plan
/reject <plan_id>       # Discard a pending plan
/plan <plan_id>         # View plan details
/cancel_workflow        # Cancel running workflow
```

### Phase 2 Architecture

**New Components:**

| Component | File | Purpose |
|-----------|------|---------|
| Plan Structure | `plan.py` | Data models for plans and steps |
| Plan Parser | `plan_parser.py` | Extract plans from agent responses |
| Workflow Engine | `workflow_engine.py` | Execute plans with rollback |
| Approval UI | `plan_approval.py` | Interactive approval interface |

**Integration Points:**

- `multi_agent_orchestrator.py` - Automatic plan detection
- `tool_executor.py` - Tool execution for workflow steps
- `output_manager.py` - Progress visualization
- `agent_manager.py` - Sub-agent coordination

### Phase 2 Features

✅ **Plan Parsing** - Extract `[PLAN]` tags from agent responses
✅ **Dependency Resolution** - Topological sort for correct execution order
✅ **Validation** - Detect circular dependencies, invalid agents/tools
✅ **Progress Tracking** - Real-time visual indicators (✓ ○ ⟳ ✗)
✅ **Checkpointing** - Backup files before modification
✅ **Rollback** - Restore state on failures
✅ **Cost Estimation** - Calculate API costs before execution
✅ **Time Estimation** - Predict workflow duration
✅ **Retry Logic** - Auto-retry failed steps (up to 3 attempts)
✅ **Pause/Resume** - Control workflow execution
✅ **State Persistence** - Save/load workflow state

### Testing

Phase 2 includes 23 automated tests:

```bash
python3 test_phase2.py

# Results: 23/23 tests passing (100%)
# Coverage: Plans, Parser, Engine, Integration
```

See `PHASE2_TESTING.md` and `PHASE2_TEST_REPORT.md` for details.

### Cost Optimization with Workflows

Workflows enable additional cost savings:

| Task Type | Before Workflows | With Workflows | Savings |
|-----------|------------------|----------------|---------|
| 5-step implementation | 5×120b calls | 1×120b + 4×20b | ~70% |
| Review + Test cycle | 3×120b calls | 1×120b + 2×20b | ~60% |
| Batch file processing | N×120b calls | 1×120b + N×20b | ~80% |

**How it works:**
- Main agent (120b) creates the plan
- Sub-agents (20b) execute individual steps
- Execution is automated, no manual coordination
- Costs estimated upfront for approval

### Example: Automated Testing Workflow

```
You: Implement user authentication with tests

[Main agent creates workflow]

======================================================================
  WORKFLOW PLAN: User Authentication Implementation
======================================================================

📊 Summary:
   Steps: 4
   Estimated Time: 5m 30s
   Estimated Cost: $0.08

📝 Steps:
   1. Research authentication best practices (researcher, 60s)
   2. Implement auth module (implementer, 180s)
   3. Write unit tests (tester, 90s)
   4. Run tests and verify (tester, 60s)

======================================================================

Your decision [A/R/M]: A

🚀 Executing workflow...

[Progress tracking shows each step completing]

✅ Workflow completed successfully!
All tests passing (15/15)
```

### Migration from Phase 1

No breaking changes! Phase 2 is fully backward compatible:
- All Phase 1 features still work
- Manual agent spawning unchanged
- Existing configurations compatible
- Workflows are opt-in (agents propose them)

### Phase 2 Limitations

Current limitations (planned for Phase 3):
- ⚠️ Workflows execute in main agent thread (no parallel step execution yet)
- ⚠️ No workflow templates (each plan is custom)
- ⚠️ File rollback only (no database transaction support)
- ⚠️ No plan modification UI (approve/reject only)

## Future Enhancements (Phase 3+)

### Planned for Phase 3
- [ ] Multi-agent step execution (distribute steps to sub-agents)
- [ ] Workflow templates and reusability
- [ ] Advanced rollback (database transactions, API rollback)
- [ ] Plan modification interface
- [ ] Agent-to-agent direct communication during workflows

### Future Ideas
- [ ] Agent-to-agent communication (beyond summaries)
- [ ] Persistent agent sessions
- [ ] Agent learning from past interactions
- [ ] Web UI for agent visualization
- [ ] Agent performance metrics and optimization
- [ ] Integration with external tools (web search, code execution)

## Support

For issues or questions:
- Check logs in `agent_debug.log` and `logs/` directory
- Verify API connectivity with single-agent system first
- Ensure aiohttp is installed correctly
- Review agent status with `/agents` and `/stats` commands

---

Built on top of the streaming coding agent framework with async/await concurrency.
