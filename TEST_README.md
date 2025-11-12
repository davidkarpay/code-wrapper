# File Operations Testing - Quick Start Guide

## Overview
This directory contains a comprehensive test suite for the coding_agent_streaming.py file operations capabilities.

## Files Created

### Test Environment
- **`test_workspace/`** - Test directory with sample files
  - `test_read.txt` (185 bytes) - Small file for READ testing
  - `test_edit.txt` (238 bytes) - File for EDIT testing
  - `test_read_large.txt` (600 KB) - Large file to test size limits

### Documentation
- **`test_plan.md`** - Comprehensive test plan with 30 test cases across 8 phases
- **`test_results.md`** - Template for recording test results
- **`TEST_README.md`** - This file

## Quick Start

### 1. Review the Test Plan
```bash
cat test_plan.md
```
or open in your editor to see all 30 test cases.

### 2. Start the Agent
```bash
python coding_agent_streaming.py
```

### 3. Run Tests Interactively
Follow the test plan and execute each test by:
- Using CLI commands (e.g., `/ls`, `/read`, `/config`)
- Asking the LLM to perform file operations
- Observing the plan approval workflow
- Recording results in `test_results.md`

### 4. Monitor Logs
In another terminal:
```bash
tail -f agent_debug.log
```

## Test Categories

### Phase 1: CLI Commands (4 tests)
Test direct commands like `/ls`, `/read`, `/config`

### Phase 2: FILE_READ Operations (4 tests)
- Read existing files
- Read non-existent files
- Test size limits
- Test directory restrictions

### Phase 3: FILE_WRITE Operations (4 tests)
- Create new files
- Overwrite with warnings
- Test size limits
- Test permission toggles

### Phase 4: FILE_EDIT Operations (4 tests)
- Find and replace text
- Test with non-existent text
- Verify backup creation
- Read backup files

### Phase 5: Plan Mode Workflow (4 tests)
- Approve plans
- Reject plans
- Modify plans
- Toggle plan mode

### Phase 6: Security Controls (4 tests)
- Directory restrictions
- Path traversal protection
- Symlink handling
- Size limit boundaries

### Phase 7: Error Handling (3 tests)
- Multiple operations
- Partial failures
- Unicode support

### Phase 8: Verification (3 tests)
- List all created files
- Check debug logs
- Verify backups

## Important Notes

### What IS Supported
✅ **FILE_READ** - Read files with size/directory restrictions
✅ **FILE_WRITE** - Create/overwrite files with warnings
✅ **FILE_EDIT** - Find/replace with automatic backups
✅ **Plan Mode** - Approval workflow before execution
✅ **Security** - Directory restrictions, size limits, permissions

### What IS NOT Supported
❌ **FILE_DELETE** - No delete operation exists
❌ **FILE_RENAME** - No rename operation
❌ **FILE_COPY** - No copy operation

### Current Configuration
- **Max file size:** 500 KB
- **Plan mode:** Enabled (requires approval)
- **Backup on edit:** Enabled
- **Overwrite warning:** Enabled
- **Allowed directories:**
  - Current directory (`.`)
  - `./agent_workspace`
  - `./projects`
  - `./data`
  - `./output`
  - `./research`
  - `./templates`
  - `./test_workspace`

## Example Test Session

```
# Start agent
python coding_agent_streaming.py

# Test 1: List test files
You: /ls test_workspace

# Test 2: Read a file directly
You: /read test_workspace/test_read.txt

# Test 3: Ask agent to read a file
You: Please read the file test_workspace/test_read.txt

# Agent will propose a plan, you approve with:
yes

# Test 4: Test size limit
You: /read test_workspace/test_read_large.txt
# Should fail: File too large

# Test 5: Create a new file
You: Please create test_workspace/my_test.txt with content "Hello World"
# Approve the plan when prompted

# Test 6: Edit a file
You: Please edit test_workspace/test_edit.txt and replace "OLD_VALUE" with "NEW_VALUE"
# Approve the plan, verify backup created

# Continue with remaining tests...
```

## Recording Results

As you run each test:

1. Open `test_results.md`
2. Find the corresponding test section
3. Mark [ ] PASS or [X] FAIL
4. Record actual behavior
5. Copy relevant log excerpts
6. Note any unexpected behavior

## Success Criteria

All tests should:
- ✅ Execute without crashes
- ✅ Enforce security restrictions
- ✅ Provide clear error messages
- ✅ Log operations correctly
- ✅ Create backups for edits
- ✅ Respect permission flags
- ✅ Work within plan mode workflow

## Troubleshooting

### Agent not finding files
- Ensure you're using relative paths from the current directory
- Check `allowed_directories` in config
- Use `/ls` to verify files exist

### Operations not executing
- Check if plan mode is enabled (`/config`)
- Approve plans when prompted
- Check permission flags are enabled

### Size limit errors
- Expected for files > 500KB
- Can be adjusted in `agent_config.json` (`max_file_size_kb`)

### Path permission errors
- Expected for paths outside `allowed_directories`
- Add directories to config if needed

## Next Steps

1. ✅ Review `test_plan.md` thoroughly
2. ✅ Start agent and verify configuration (`/config`)
3. ✅ Execute tests in order
4. ✅ Record results in `test_results.md`
5. ✅ Check `agent_debug.log` for issues
6. ✅ Compile summary of findings
7. ✅ Document any bugs or improvements

## Questions?

Refer to:
- `test_plan.md` - Full test specifications
- `agent_debug.log` - Detailed operation logs
- `coding_agent_streaming.py` - Source code
- `agent_config.json` - Current configuration

Happy testing! 🧪
