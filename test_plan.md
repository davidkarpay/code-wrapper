# File Operations Testing Plan

## Overview
Comprehensive testing of the coding_agent_streaming.py file operation capabilities including READ, WRITE, EDIT operations and all security controls.

**Note:** DELETE operation does not exist in this agent.

## Test Environment Setup

### Test Files Created
- `./test_workspace/test_read.txt` (185 bytes) - For READ operation testing
- `./test_workspace/test_edit.txt` (238 bytes) - For EDIT operation testing
- `./test_workspace/test_read_large.txt` (600KB) - For size limit testing

### Current Configuration
- Provider: ollama
- Model: gpt-oss:120b-cloud
- Plan mode: True
- File operations permissions: All enabled (read/write/edit)
- Max file size: 500KB
- Allowed directories: ".", "./agent_workspace", "./projects", "./data", "./output", "./research", "./templates", "./test_workspace"

---

## Test Suite

### Phase 1: CLI Commands Testing
Test the direct CLI commands before testing LLM-driven operations.

#### Test 1.1: /ls Command
```
You: /ls test_workspace
Expected: Shows list of 3 test files with sizes
```

#### Test 1.2: /read Command (Direct)
```
You: /read test_workspace/test_read.txt
Expected: Displays file contents (185 bytes)
```

#### Test 1.3: /read Large File
```
You: /read test_workspace/test_read_large.txt
Expected: ERROR - File too large (600KB > 500KB limit)
```

#### Test 1.4: /config Command
```
You: /config
Expected: Shows current configuration including permissions
```

---

### Phase 2: FILE_READ Operations (LLM-Driven)

#### Test 2.1: Read Existing Small File
```
You: Please read the file test_workspace/test_read.txt
Expected: Agent uses [FILE_READ] tag, successfully reads and displays content
```

#### Test 2.2: Read Non-Existent File
```
You: Please read the file test_workspace/does_not_exist.txt
Expected: Agent uses [FILE_READ] tag, returns error "File does not exist"
```

#### Test 2.3: Read Large File (Size Limit)
```
You: Please read the file test_workspace/test_read_large.txt
Expected: Agent uses [FILE_READ] tag, returns error "File too large: 600.0KB (max: 500KB)"
```

#### Test 2.4: Read File Outside Allowed Directories
*First, toggle permissions to test:*
```
You: /read /etc/passwd
Expected: ERROR - "Path /etc/passwd is not in allowed directories"
```

---

### Phase 3: FILE_WRITE Operations (LLM-Driven)

#### Test 3.1: Create New File
```
You: Please create a new file called test_workspace/test_write_new.txt with content "Hello, this is a test file created by the agent."

Expected:
- Agent proposes [PLAN] (if plan_mode=true)
- User approves
- Agent uses [FILE_WRITE] tag
- File created successfully
```

#### Test 3.2: Overwrite Existing File (With Warning)
```
You: Please write to the file test_workspace/test_read.txt and replace its content with "OVERWRITTEN CONTENT"

Expected:
- Agent proposes [PLAN]
- User approves
- Agent uses [FILE_WRITE] tag
- Overwrite warning prompt appears
- User confirms
- File overwritten
```

#### Test 3.3: Write File with Content >500KB
```
You: Please create a file test_workspace/test_write_large.txt containing 600KB of the letter 'A'

Expected:
- Agent proposes [PLAN]
- User approves
- Agent uses [FILE_WRITE] tag
- ERROR: "Content too large: 600.0KB (max: 500KB)"
```

#### Test 3.4: Toggle Write Permission Off
```
You: /allow_write
(Toggles write permission off)

You: Please create a file test_workspace/test_permission.txt with content "Test"

Expected:
- Agent proposes [PLAN]
- User approves
- Agent uses [FILE_WRITE] tag
- ERROR: "File writing is disabled in configuration"

Then toggle back on:
You: /allow_write
```

---

### Phase 4: FILE_EDIT Operations (LLM-Driven)

#### Test 4.1: Edit File with Find/Replace
```
You: Please edit the file test_workspace/test_edit.txt and replace "OLD_VALUE" with "UPDATED_VALUE"

Expected:
- Agent proposes [PLAN]
- User approves
- Agent uses [FILE_EDIT] tag
- Backup file created: test_edit.txt.backup
- Text successfully replaced
```

#### Test 4.2: Edit with Non-Existent Find Text
```
You: Please edit the file test_workspace/test_edit.txt and replace "NONEXISTENT_TEXT" with "SOMETHING"

Expected:
- Agent proposes [PLAN]
- User approves
- Agent uses [FILE_EDIT] tag
- ERROR: "Text to replace not found in file"
```

#### Test 4.3: Verify Backup File Created
```
You: /ls test_workspace

Expected: Should show test_edit.txt.backup file
```

#### Test 4.4: Read Backup File
```
You: /read test_workspace/test_edit.txt.backup

Expected: Shows original content before edit
```

---

### Phase 5: Plan Mode Workflow Testing

#### Test 5.1: Plan Approval
```
You: Please create three files: test1.txt, test2.txt, test3.txt in test_workspace

Expected:
- Agent generates [PLAN] tag with description
- Plan approval prompt appears
- User types: yes
- Agent executes [FILE_WRITE] operations for all 3 files
- All files created successfully
```

#### Test 5.2: Plan Rejection
```
You: Please delete all files in test_workspace (Note: should fail as delete not supported)

Expected:
- Agent proposes [PLAN] (or explains delete not available)
- User types: no
- Plan rejected, no operations executed
```

#### Test 5.3: Plan Modification
```
You: Please create a file test_workspace/test_modify.txt with content "Original"

Expected:
- Agent proposes [PLAN]
- User types: modify
- Prompt: "Please describe the changes you want:"
- User types: "Change the content to 'Modified Content'"
- Agent re-proposes modified plan
- User approves
- File created with modified content
```

#### Test 5.4: Toggle Plan Mode Off
```
You: /plan
(Toggles plan mode off)

You: Please create test_workspace/test_no_plan.txt with content "No plan needed"

Expected:
- No plan approval prompt
- Agent directly executes [FILE_WRITE]
- File created immediately

Then toggle back on:
You: /plan
```

---

### Phase 6: Security Controls Testing

#### Test 6.1: Directory Restrictions
```
You: Please read the file /tmp/test.txt

Expected: ERROR - "Path /tmp/test.txt is not in allowed directories"
```

#### Test 6.2: Path Traversal Attack
```
You: Please read the file ../../../etc/passwd

Expected: ERROR - Path validation should block this
```

#### Test 6.3: Symlink Handling
*Create a symlink first via CLI:*
```bash
ln -s /etc/passwd test_workspace/link_to_passwd
```

Then test:
```
You: Please read test_workspace/link_to_passwd

Expected: ERROR - Resolved path should be outside allowed directories
```

#### Test 6.4: Size Limit Boundary (Exactly 500KB)
*Create exactly 500KB file:*
```bash
python3 -c "with open('test_workspace/test_500kb.txt', 'w') as f: f.write('X' * (500 * 1024))"
```

Then test:
```
You: Please read test_workspace/test_500kb.txt

Expected: SUCCESS (exactly at limit) or ERROR depending on >= vs > check
```

---

### Phase 7: Error Handling & Edge Cases

#### Test 7.1: Multiple Operations in Sequence
```
You: Please:
1. Read test_workspace/test_read.txt
2. Create test_workspace/multi_test.txt with content "Step 2"
3. Edit test_workspace/multi_test.txt replacing "Step 2" with "Step 3"

Expected:
- Agent proposes [PLAN] with all operations
- User approves
- All operations execute in sequence
- Success count: 3, Failure count: 0
```

#### Test 7.2: Partial Failure Handling
```
You: Please:
1. Read test_workspace/test_read.txt (should succeed)
2. Read test_workspace/does_not_exist.txt (should fail)
3. Create test_workspace/final_test.txt with content "Done" (should succeed)

Expected:
- Agent proposes [PLAN]
- User approves
- Operation 1: SUCCESS
- Operation 2: FAILURE (file not found)
- Operation 3: SUCCESS
- Success count: 2, Failure count: 1
```

#### Test 7.3: File with Unicode Characters
```
You: Please create test_workspace/unicode_test.txt with content "Hello 世界 🌍 Émojis and Unicode!"

Expected:
- Agent proposes [PLAN]
- User approves
- File created with UTF-8 encoding
- Can be read back correctly
```

---

### Phase 8: Verification & Cleanup

#### Test 8.1: Verify All Created Files
```
You: /ls test_workspace

Expected: Shows all files created during testing
```

#### Test 8.2: Check Debug Log
```bash
tail -100 agent_debug.log
```

Expected: All file operations logged with details

#### Test 8.3: Verify Backup Files
```
You: /ls test_workspace | grep backup

Expected: Shows .backup files for edited files
```

---

## Test Execution Instructions

1. **Start the agent:**
   ```bash
   python coding_agent_streaming.py
   ```

2. **Run each test in order**, recording results in `test_results.md`

3. **For each test, note:**
   - Test number and description
   - Commands/prompts used
   - Expected outcome
   - Actual outcome
   - Pass/Fail status
   - Any errors or unexpected behavior
   - Relevant log excerpts

4. **Check logs after each significant test:**
   ```bash
   tail -50 agent_debug.log
   ```

5. **Document any deviations** from expected behavior

---

## Success Criteria

- ✅ All READ operations work within security constraints
- ✅ All WRITE operations work with proper warnings
- ✅ All EDIT operations work with backup creation
- ✅ Directory restrictions properly enforced
- ✅ Size limits properly enforced
- ✅ Permission toggles work correctly
- ✅ Plan mode workflow functions properly
- ✅ Error messages are clear and helpful
- ✅ Operations log correctly to agent_debug.log
- ✅ No operations succeed when they should fail
- ✅ No crashes or unhandled exceptions

---

## Known Limitations

1. **No DELETE operation** - Cannot test file deletion
2. **No RENAME operation** - Cannot test file renaming
3. **No COPY operation** - Cannot test file copying
4. **CLI /read command** bypasses plan mode - Direct read doesn't require approval

---

## Next Steps

After completing all tests, compile results into `test_results.md` with:
- Summary of pass/fail rates
- List of any bugs found
- Recommendations for improvements
- Log file excerpts for failed tests
