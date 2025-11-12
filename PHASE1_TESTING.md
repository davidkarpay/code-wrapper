# Phase 1 Testing Guide

## What's Been Implemented

Phase 1 adds three critical capabilities to Code Wrapper's subagent system:

1. **Automatic Agent Spawning** - Agents spawn automatically when keywords are detected
2. **Tool Execution** - Agents can run bash commands and Python scripts safely
3. **File Operations** - Agents can read and write files within allowed directories

## Testing Automatic Agent Spawning

### Test 1: Keyword-Based Spawning

```bash
# Start the multi-agent system
python multi_agent_orchestrator.py

# Type messages with keywords to trigger auto-spawning
You: Please review the authentication module for security issues

# Expected: reviewer_agent should spawn automatically
# You should see: 🚀 Auto-spawning reviewer agent (keyword: 'review')...

You: Can you test the login flow?

# Expected: tester_agent should spawn automatically
# You should see: 🚀 Auto-spawning tester agent (keyword: 'test')...

You: Research best practices for JWT authentication

# Expected: researcher_agent should spawn automatically
# You should see: 🚀 Auto-spawning researcher agent (keyword: 'research')...
```

### Test 2: Toggle Auto-Spawning

```bash
# Check current status
/auto_spawn

# Should toggle and show: ❌ Automatic sub-agent spawning disabled

# Try keyword - should NOT spawn agent
You: Review this code

# Toggle back on
/auto_spawn

# Should show: ✅ Automatic sub-agent spawning enabled
```

### Test 3: Multiple Keywords

```bash
You: Please research and analyze the security vulnerabilities in the auth system

# Expected: Both researcher_agent AND tester_agent may spawn
# (depends on keyword matching logic)
```

## Testing Tool Execution

### Prerequisites

1. Ensure your `agent_config_multi_agent.json` has proper allowed_directories:

```json
"file_operations": {
  "allow_file_write": true,
  "allow_file_read": true,
  "allowed_directories": [
    "./agent_workspace",
    "./test_workspace",
    "./projects"
  ]
}
```

2. Create test workspace:

```bash
mkdir -p agent_workspace test_workspace
```

### Test 4: Bash Command Execution

The agents now have access to these methods:
- `execute_bash(command, working_dir, timeout)` - Run bash commands
- `execute_python_script(script_path, args, timeout)` - Run Python scripts
- `read_file_tool(file_path)` - Read files
- `write_file_tool(file_path, content, overwrite)` - Write files
- `list_files_tool(directory, pattern)` - List files

**Note:** Agents can call these methods directly if they understand they have access to them. This requires updating the system prompts to inform agents about their capabilities.

### Test 5: File Operations Safety

Test that safety mechanisms work:

1. **Allowed Directory Enforcement**
   - Agents should only access files in allowed_directories
   - Attempts to access other directories should fail with error message

2. **Safe Mode Command Filtering**
   - Dangerous commands (rm, sudo, etc.) should be blocked
   - Safe commands (ls, cat, grep, python3) should work

3. **File Size Limits**
   - Files larger than max_file_size_kb should be rejected

## Test Scenarios

### Scenario 1: Documentation Agent Workflow

```bash
You: Please research Python testing best practices and write a summary to test_workspace/testing_best_practices.md
```

**Expected Behavior:**
1. Researcher agent spawns (keyword: research)
2. Agent gathers information (from its LLM knowledge)
3. Agent uses `write_file_tool()` to create the document
4. Success message with file path

**Verification:**
```bash
ls -la test_workspace/
cat test_workspace/testing_best_practices.md
```

### Scenario 2: Test Runner Agent

Create a simple test script:

```bash
cat > test_workspace/sample_test.py << 'EOF'
#!/usr/bin/env python3
print("Running tests...")
print("Test 1: PASS")
print("Test 2: PASS")
print("Test 3: FAIL")
print("Tests complete!")
exit(1)  # Non-zero exit for failed test
EOF

chmod +x test_workspace/sample_test.py
```

Then ask the agent:

```bash
You: Please test the sample_test.py script in test_workspace and analyze the results
```

**Expected Behavior:**
1. Tester agent spawns (keyword: test)
2. Agent uses `execute_python_script()` to run the test
3. Agent reports return code, stdout, stderr
4. Agent analyzes which tests passed/failed

### Scenario 3: Code Review with File Reading

Create a code file to review:

```bash
cat > test_workspace/auth.py << 'EOF'
def authenticate(username, password):
    # TODO: This is insecure - storing plaintext passwords!
    if username == "admin" and password == "admin123":
        return True
    return False
EOF
```

Then:

```bash
You: Please review the auth.py file in test_workspace for security issues
```

**Expected Behavior:**
1. Reviewer agent spawns (keyword: review)
2. Agent uses `read_file_tool()` to read auth.py
3. Agent identifies security vulnerabilities
4. Agent provides recommendations

## Verifying Implementation

### Check 1: Verify Automatic Spawning Code

```bash
grep -A 20 "check_and_auto_spawn" multi_agent_orchestrator.py
```

Should show the keyword detection logic.

### Check 2: Verify ToolExecutor Integration

```bash
grep "tool_executor" async_streaming_agent.py | head -10
```

Should show ToolExecutor is imported and used.

### Check 3: Verify Config is Loaded

```bash
grep "spawning_rules" agent_config_multi_agent.json
```

Should show keyword mappings and auto_spawn_on_keywords setting.

## Troubleshooting

### Agent Not Spawning Automatically

**Check:**
1. Is auto_spawn_on_keywords true in config?
2. Use `/auto_spawn` to check if it's enabled
3. Verify keyword is in spawning_rules.keywords
4. Check orchestrator logs

### Tool Execution Failing

**Check:**
1. Is the path in allowed_directories?
2. Is the command in the safe_bash_commands whitelist?
3. Check tool executor logs
4. Verify file permissions

### File Operations Not Working

**Check:**
1. allow_file_write / allow_file_read settings in config
2. Directory exists and is writable
3. File size under max_file_size_kb limit
4. Path is within allowed_directories

## Success Criteria

Phase 1 is successful if:

- ✅ Agents spawn automatically when keywords are detected
- ✅ `/auto_spawn` command toggles the feature
- ✅ Agents can execute safe bash commands
- ✅ Agents can run Python scripts
- ✅ Agents can read/write files in allowed directories
- ✅ Dangerous commands are blocked
- ✅ File size limits are enforced
- ✅ Directory restrictions are enforced

## Next Steps

After verifying Phase 1 works:

- **Phase 2**: Implement workflow engine for multi-step plan execution
- **Phase 3**: Add workflow chaining and coordination between agents

## Known Limitations

1. **Agents don't auto-discover tools**: System prompts need updating to tell agents about available methods
2. **No function calling**: Agents can't automatically invoke tools - requires manual calling in code or prompt engineering
3. **No plan approval yet**: Phase 2 will add this
4. **No inter-agent coordination yet**: Phase 3 will add this

## Recommended Enhancements for Phase 1

Before moving to Phase 2, consider:

1. Update system prompts in `prompts/*.txt` to inform agents about tool capabilities
2. Add examples in prompts showing how to request tool usage
3. Create wrapper commands like `/run-script` for easier tool access
4. Add better logging/debugging output for tool execution
