# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a streaming AI coding assistant that connects to LLM providers (LM Studio or Ollama) for local or cloud LLM inference. It provides real-time streaming responses with visible "thinking" processes, making it ideal for proof-of-concept development and understanding how AI models reason through problems.

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
- Handles both streaming and non-streaming API requests to LM Studio or Ollama
- Implements special "thinking" tag parsing to visualize model reasoning
- Provides token count statistics and performance metrics
- Supports API authentication for cloud-based models

**Configuration System**
- `agent_config.json`: Primary configuration for provider selection, API connection, model settings, and agent behavior
- `agent_config_ollama_cloud.json`: Pre-configured template for Ollama cloud usage
- `system_prompt.txt`: Customizable system prompt loaded at agent initialization
- All settings can be modified at runtime via CLI commands
- See `PROVIDER_SETUP.md` for detailed provider configuration instructions

**Thinking Visualization**
The agent parses special `[THINKING]...[/THINKING]` and `[RESPONSE]...` tags in model outputs to separate reasoning from final answers. This allows users to see the model's step-by-step reasoning process before the actual response.

### Provider Integration

The agent supports multiple LLM providers with OpenAI-compatible APIs:

**LM Studio (Local)**
- Default endpoint: `http://localhost:1234/v1`
- No API key required
- Example model: `TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF`

**Ollama (Local or Cloud)**
- Local endpoint: `http://localhost:11434/v1`
- Cloud endpoint: `https://ollama.com/v1`
- Cloud requires API key (set in config)
- Example model: `gpt-oss:120b-cloud`

All providers use:
- `/chat/completions` endpoint with streaming support
- Server-Sent Events (SSE) for real-time token streaming
- Bearer token authentication (when API key is provided)

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

---

## Multi-Agent System (NEW!)

The repository now includes a **multi-agent orchestration system** that enables concurrent execution of multiple AI agents with different model sizes for cost optimization and parallel task execution.

### Quick Start

```bash
# Install async dependencies
pip install -r requirements_multi_agent.txt

# Run the multi-agent system
python multi_agent_orchestrator.py
# or use the quick start script
./run_multi_agent.sh
```

### Architecture

```
Main Agent (gpt-oss:120b-cloud)
    ├── Reviewer Agent (gpt-oss:20b-cloud)
    ├── Researcher Agent (gpt-oss:20b-cloud)
    ├── Implementer Agent (gpt-oss:20b-cloud)
    ├── Tester Agent (gpt-oss:20b-cloud)
    └── Optimizer Agent (gpt-oss:20b-cloud)
```

### Key Features

**1. Concurrent Execution**
- Multiple agents work in parallel using async/await
- Non-blocking I/O with aiohttp
- Thread-safe file operations

**2. Role Specialization**
- **Main Agent**: Orchestration and complex reasoning (120b model)
- **Reviewer**: Code review and security analysis (20b model)
- **Researcher**: Information gathering and documentation (20b model)
- **Implementer**: Code writing and feature implementation (20b model)
- **Tester**: Testing and validation (20b model)
- **Optimizer**: Performance optimization (20b model)

**3. Context Isolation**
- Each agent maintains separate conversation history
- Sub-agents send summaries back to main agent
- Prevents context pollution while enabling coordination

**4. Cost Optimization**
- Use large models (120b) only for complex orchestration
- Use smaller models (20b) for specialized subtasks
- Potential savings of 50-80% on API costs

### Multi-Agent Commands

```bash
# Spawn specialized agents
/spawn reviewer Review the authentication module for security
/spawn researcher Find best practices for async Python database connections
/spawn implementer Implement JWT token validation
/spawn tester Test the user registration flow
/spawn optimizer Analyze performance bottlenecks

# Manage agents
/agents          # List all active agents
/stop <agent_id> # Stop a specific agent
/stop_all        # Stop all sub-agents
/stats           # Show system statistics

# Direct communication
@<agent_id> message  # Send message to specific agent
```

### Configuration Files

- **`agent_config_multi_agent.json`**: Multi-agent configuration with role profiles
- **`prompts/*.txt`**: Role-specific system prompts
- **`secrets.json`**: API keys (create from template)

### Example Workflow

```
You: I need to implement user authentication with security best practices

[Main agent plans the approach]

You: /spawn researcher Research JWT authentication security best practices

[Researcher gathers information and sends summary]

You: /spawn implementer Implement JWT authentication based on the research

[Implementer writes the code]

You: /spawn reviewer Review the authentication code for security issues

[Reviewer analyzes and provides feedback]

You: /spawn tester Test the authentication implementation

[Tester validates the code]

[Main agent coordinates all summaries and suggests next steps]
```

### Key Implementation Files

- **`multi_agent_orchestrator.py`**: Main entry point and event loop
- **`agent_manager.py`**: Agent lifecycle and coordination
- **`output_manager.py`**: Multiplexed output handling
- **`async_streaming_agent.py`**: Async agent implementation
- **`MULTI_AGENT_README.md`**: Detailed documentation

### Technical Architecture

The multi-agent system extends the single-agent architecture with:

1. **AgentManager**: Tracks agent registry, status, and inter-agent communication
2. **OutputManager**: Provides visual separation and prevents output collision
3. **AsyncStreamingAgent**: Async version of StreamingAgent with concurrent execution
4. **Summary System**: `[SUMMARY]...[/SUMMARY]` tags for condensed information flow

### When to Use Multi-Agent vs Single-Agent

**Use Multi-Agent When:**
- Task requires multiple specialized perspectives (review, test, optimize)
- Parallel execution can speed up workflow
- Cost optimization is important (use smaller models for subtasks)
- Complex projects benefit from modular agent roles

**Use Single-Agent When:**
- Simple, straightforward tasks
- Sequential conversation flow
- Working with local models only (no API costs)
- Learning or experimenting with the system

### Cost Analysis

Example scenario: Implementing a feature with review and testing

| Approach | API Calls | Estimated Cost |
|----------|-----------|----------------|
| Single 120b agent | 5 requests × 120b | 100% |
| Multi-agent (1×120b + 2×20b) | 1×120b + 2×20b | ~40% |

*Assuming 20b model is ~6x cheaper than 120b*

For more details, see `MULTI_AGENT_README.md`.

---

## Workflow Engine - Phase 2 (NEW!)

The multi-agent system now includes a **Workflow Engine** that enables agents to propose multi-step execution plans, get user approval, and execute them with progress tracking, error handling, and automatic rollback.

### Quick Start

The workflow engine is integrated into the multi-agent orchestrator. When agents propose multi-step plans, they are automatically detected, displayed for approval, and executed:

```bash
python multi_agent_orchestrator.py

You: Create a test file, then read it back and display the contents

[Main agent proposes a workflow plan with 2 steps]

✨ Agent proposed a workflow plan: File Creation and Verification

[Plan displayed with steps, estimated time, and cost]

Your decision [A/R/M/V]: A

[Plan executes with real-time progress tracking]

✅ Workflow completed successfully!
```

### Phase 2 Features

#### 1. **Workflow Plans**
- Agents can propose multi-step plans with dependencies
- Each step specifies: description, agent, tool, arguments, estimated time
- Plans include cost estimates and total execution time
- Dependency resolution ensures correct execution order

#### 2. **Plan Approval Workflow**
- Interactive approval UI displays plan details
- Options: Approve, Reject, Modify, or View again
- Validation checks for circular dependencies and invalid configurations
- Final confirmation before execution for risky operations

#### 3. **Execution Engine**
- Sequential execution respecting step dependencies
- Real-time progress tracking with visual indicators (✓ ○ ⟳ ✗)
- Checkpoint creation before file modifications
- Automatic rollback on failures
- Retry logic (up to 3 attempts per step)
- Pause/resume/cancel capabilities

#### 4. **Error Handling & Rollback**
- Checkpoints created before risky operations
- Automatic file backups before modifications
- Transaction-like rollback on failures
- All changes reversed if execution fails

### Workflow Commands

Available in the multi-agent orchestrator:

```bash
/plans                  # List all pending workflow plans
/approve <plan_id>      # Approve and execute a specific plan
/reject <plan_id>       # Reject a pending plan
/plan <plan_id>         # View detailed plan information
/cancel_workflow        # Cancel currently running workflow
```

### Plan Format

Agents create plans using the `[PLAN]...[/PLAN]` tag format:

```
[PLAN]
## Workflow: Create and Test Feature

### Step 1: Write implementation
- Agent: implementer
- Tool: write_file_tool
- Arguments: {"path": "./feature.py", "content": "..."}
- Dependencies: none
- Estimated Time: 60s

### Step 2: Run tests
- Agent: tester
- Tool: execute_bash
- Arguments: {"command": "python3 -m pytest ./tests/test_feature.py"}
- Dependencies: Step 1
- Estimated Time: 30s

## Total Estimated Time: 90s
## Cost Estimate: $0.04
[/PLAN]
```

### Example Workflow

```
You: Implement a hello world script and test it

[Main agent creates a 2-step plan]

======================================================================
  WORKFLOW PLAN: Hello World Implementation
======================================================================

Description: Create and test a simple hello world script

📊 Summary:
   Steps: 2
   Estimated Time: 1m 30s
   Estimated Cost: $0.04

📝 Execution Steps:
----------------------------------------------------------------------

○ Step 1: Create hello.py script
   Agent: implementer
   Tool: write_file_tool
   Time: ~60s

○ Step 2: Execute and verify output
   Agent: tester
   Tool: execute_bash
   Dependencies: Step 1
   Time: ~30s

======================================================================

Options:
  [A] Approve - Execute this plan
  [R] Reject - Cancel this plan
  [M] Modify - Request changes
  [V] View - Display details again

Your decision [A/R/M/V]: A

✓ Plan approved for execution

🚀 Executing workflow: Hello World Implementation

[12:34:56] ⟳ Creating hello.py script...
[12:34:57] ✓ Completed in 0.8s
[12:34:57] ⟳ Execute and verify output...
[12:34:58] ✓ Completed in 0.5s

======================================================================
  EXECUTION SUMMARY
======================================================================

Plan: Hello World Implementation
Status: COMPLETED

Progress: 2/2 steps completed
Time: 1m 18s
Checkpoints: 1 created

======================================================================

✅ Workflow completed successfully!
```

### Architecture

**Key Components:**

- **`plan.py`** - Plan and PlanStep data structures with validation
- **`plan_parser.py`** - Extracts and parses `[PLAN]` tags from agent responses
- **`workflow_engine.py`** - Executes plans with progress tracking and rollback
- **`plan_approval.py`** - Interactive approval UI with visual display

**Integration:**

- Workflow engine integrated into `multi_agent_orchestrator.py`
- Automatic plan detection in agent responses
- Tool execution via existing `tool_executor.py`
- Progress callbacks to `output_manager.py`

### Testing

Phase 2 includes comprehensive testing:

```bash
# Run Phase 2 tests
python3 test_phase2.py

# Results: 23/23 tests passing (100% pass rate)
```

See `PHASE2_TESTING.md` and `PHASE2_TEST_REPORT.md` for details.

### Cost Optimization

Workflows enable further cost optimization:

| Scenario | Single Agent | Multi-Agent | With Workflows | Savings |
|----------|--------------|-------------|----------------|---------|
| 5-step task | 5×120b | 1×120b + 2×20b | 1×120b + 4×20b | ~70% |
| Review + Test | 3×120b | 1×120b + 2×20b | 1×120b + 2×20b | ~60% |

**Workflow Benefits:**
- Main agent (120b) only plans, doesn't execute
- Sub-agents (20b) execute individual steps
- Parallel execution where possible
- Automatic cost estimation before approval

### Use Cases

**Perfect for:**
- Multi-step file operations (create, modify, test)
- Code implementation with testing and review
- Data processing pipelines
- Build and deployment workflows
- Batch operations across multiple files

**Not ideal for:**
- Simple single-step tasks
- Highly interactive workflows requiring user input at each step
- Tasks requiring real-time decision making

### Documentation

- **`PHASE2_TESTING.md`** - Testing guide and validation results
- **`PHASE2_TEST_REPORT.md`** - Detailed test report (100% pass rate)
- **`MULTI_AGENT_README.md`** - Updated with workflow information
- System prompts updated with workflow format examples

---

## Claude Code Subagents (NEW!)

The repository now includes specialized **Claude Code subagents** implemented as slash commands to assist with documentation and testing workflows when using Claude Code (claude.ai/code) to develop this project.

### Overview

These subagents are different from the multi-agent system above. While the multi-agent system is part of the coding_agent_streaming.py application itself, these Claude Code subagents are tools for DEVELOPING and MAINTAINING the code_wrapper project using Claude Code.

### Available Subagents

#### Documentation Subagent (4 commands)

Specializes in maintaining project documentation and the test documentation website:

- **`/doc-update [file]`** - Update documentation files and regenerate HTML pages
- **`/doc-generate`** - Regenerate all HTML from markdown using generate_test_docs.py
- **`/doc-validate`** - Validate documentation consistency, links, and formatting
- **`/doc-status`** - Show documentation health metrics and last update times

#### Test Subagent (4 commands)

Specializes in test execution, analysis, and reporting:

- **`/test-run [suite]`** - Execute run_automated_tests.py and report results
- **`/test-analyze`** - Analyze test results for patterns and insights
- **`/test-report [type]`** - Generate comprehensive test reports
- **`/test-status`** - Show testing health, pass rates, and priorities

#### Git Subagent (10 commands)

Specializes in git repository management, version control, and keeping the repository synchronized and healthy:

- **`/git-status`** - Repository health check and status dashboard
- **`/git-commit`** - Smart commit with AI-generated messages and validation
- **`/git-sync`** - Intelligent sync (pull/push) with conflict detection
- **`/git-branch`** - Branch operations (create, switch, delete, list)
- **`/git-pr`** - Pull request management with GitHub CLI integration
- **`/git-merge`** - Merge orchestration with conflict resolution assistance
- **`/git-history`** - Commit history analysis and changelog generation
- **`/git-watch`** - Automated repository monitoring and alerts
- **`/git-revert`** - Safe revert operations with backup
- **`/git-cleanup`** - Branch cleanup and repository maintenance

### Usage Examples

```bash
# Documentation Commands
/doc-update test_results.md    # Update specific documentation
/doc-generate                   # Regenerate all HTML
/doc-status                     # Check documentation health

# Test Commands
/test-run                       # Run automated tests
/test-analyze                   # Analyze test results
/test-status                    # Check testing health

# Git Commands
/git-status                     # Repository health dashboard
/git-commit                     # Smart commit with AI messages
/git-sync                       # Sync with remote (pull/push)
/git-branch                     # Manage branches
/git-pr                         # Create/manage pull requests
/git-merge                      # Guided merge with conflict resolution
/git-history                    # Analyze commit history
/git-watch start                # Start repository monitoring
/git-revert HEAD                # Safely revert commits
/git-cleanup                    # Clean stale branches
```

### Subagent Coordination Protocol

The Documentation, Test, and Git subagents coordinate to keep everything synchronized:

**Test Subagent → Documentation Subagent:**
When tests complete, the test subagent hands off to documentation subagent to update documentation and regenerate HTML pages.

**Documentation Subagent → Test Subagent:**
When test plans or test documentation changes, the documentation subagent notifies the test subagent to implement or verify tests.

**Git Subagent → Test Subagent:**
Before commits, PRs, or merges, git subagent requests test validation to ensure code quality.

**Git Subagent → Documentation Subagent:**
After commits or PRs, git subagent requests documentation updates (CHANGELOG, version numbers).

**Documentation/Test Subagent → Git Subagent:**
When files are modified, documentation/test subagents notify git subagent to suggest commits.

**Git Watch → All Subagents:**
The git-watch monitoring daemon alerts relevant subagents when their domain files have uncommitted changes.

**Handoff Format:**
```
[SUBAGENT] → [SUBAGENT]

COMPLETED:
- List of completed actions

ACTION REQUIRED:
- List of required next steps

FILES MODIFIED:
- List of files changed
```

### When to Use Claude Code Subagents

**Use these subagents when:**
- Developing or maintaining the code_wrapper project with Claude Code
- Running tests and updating test documentation
- Maintaining the test-documentation website
- Managing version control and repository health
- Committing changes with semantic commit messages
- Creating pull requests and managing code reviews
- Syncing with remote repositories
- Cleaning up branches and optimizing repository
- Monitoring repository for uncommitted changes
- Ensuring documentation stays in sync with code changes
- Generating test reports, changelogs, or status summaries

**These are META tools** - they help you develop and maintain the code_wrapper project itself, rather than being part of the streaming agent application.

**Git Subagent Benefits:**
- **Automated workflows**: Smart commits with AI-generated messages
- **Safety first**: Pre-commit tests, conflict detection, automatic backups
- **Repository health**: Continuous monitoring, cleanup automation
- **GitHub integration**: Optional gh CLI support for PR management
- **Coordination**: Works with Doc and Test subagents to maintain quality

### Implementation

Subagents are implemented as slash commands in `.claude/commands/`:

**Documentation Commands:**
- `doc-update.md`, `doc-generate.md`, `doc-validate.md`, `doc-status.md`

**Test Commands:**
- `test-run.md`, `test-analyze.md`, `test-report.md`, `test-status.md`

**Git Commands:**
- `git-status.md` - Repository health dashboard
- `git-commit.md` - Smart commits with validation
- `git-sync.md` - Intelligent pull/push operations
- `git-branch.md` - Branch management
- `git-pr.md` - Pull request workflows
- `git-merge.md` - Merge and conflict resolution
- `git-history.md` - History analysis and changelog
- `git-watch.md` - Repository monitoring daemon
- `git-revert.md` - Safe revert operations
- `git-cleanup.md` - Branch and repository cleanup

Each command file contains detailed instructions for Claude Code on how to perform that specific task, including coordination protocols, error handling, safety checks, and quality validation.

**Total Subagent Commands: 22** (4 documentation + 4 test + 10 git + 4 other)
- For all projects, whenever you state a fact or proposition derived from somewhere other than your own reasoning, produce the citation.