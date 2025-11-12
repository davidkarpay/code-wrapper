---
description: Show testing health status, metrics, and priorities
allowed-tools: Bash(ls:*), Bash(cat:*), Read
---

Show testing health status, metrics, and priorities.

You are the **Test Subagent** for the code_wrapper project.

## Your Role

You provide a real-time overview of testing health, current status, and priorities for action.

## Task

Generate a comprehensive status dashboard showing the current state of all testing activities.

## Status Dashboard Components

### 1. Quick Status Overview

**At-a-glance health indicator:**

```
═══════════════════════════════════════════════════════
TESTING STATUS DASHBOARD
Timestamp: 2025-11-11 22:30:00
═══════════════════════════════════════════════════════

🎯 OVERALL HEALTH: ✅ EXCELLENT

📊 CURRENT STATUS:
   Last Test Run:   2 hours ago
   Pass Rate:       100% (20/20)
   Security:        ✅ EXCELLENT
   Coverage:        85%
   Test Health:     95/100

✅ SYSTEM STATUS: PRODUCTION READY
```

### 2. Test Suite Inventory

List all test suites and their status:

```
TEST SUITES:

📦 Main Automated Suite (run_automated_tests.py)
   Status:    ✅ PASSING
   Tests:     20
   Last Run:  2 hours ago
   Pass Rate: 100%
   Duration:  2.1 seconds

📦 Manual Test Suite (test_plan.md)
   Status:    📋 DOCUMENTED
   Tests:     30 cases
   Coverage:  8 phases
   Last Run:  Manual execution required

📦 Security Test Suite
   Status:    ✅ PASSING
   Tests:     5
   Last Run:  2 hours ago
   Pass Rate: 100%
```

### 3. Test Phase Breakdown

Status by test phase:

```
TEST PHASES:

✅ Phase 2: FILE_READ Operations
   Tests: 4/4 passing
   Coverage: Read existing, non-existent, large files, path security
   Health: Excellent

✅ Phase 3: FILE_WRITE Operations
   Tests: 4/4 passing
   Coverage: Create, overwrite, size limits, permissions
   Health: Excellent

✅ Phase 4: FILE_EDIT Operations
   Tests: 4/4 passing
   Coverage: Find/replace, validation, backup, permissions
   Health: Excellent

✅ Phase 6: Security Controls
   Tests: 3/3 passing
   Coverage: Path traversal, restrictions, boundaries
   Health: Excellent

✅ Path Validation
   Tests: 2/2 passing
   Coverage: Relative paths, normalization
   Health: Excellent

✅ Phase 8: Verification
   Tests: 3/3 passing
   Coverage: File existence, backups, listing
   Health: Excellent
```

### 4. Recent Test Activity

Timeline of recent test executions:

```
RECENT ACTIVITY:

🕐 2 hours ago
   ✅ Automated test suite executed
   Result: 20/20 passed
   Duration: 2.1s

🕐 1 day ago
   📝 Test documentation updated
   Files: test_results.md, TESTING_SUMMARY.md

🕐 3 days ago
   ✅ Manual test execution
   Result: All manual tests passed

🕐 1 week ago
   📊 Test coverage analysis
   Result: 85% coverage documented
```

### 5. Test Environment Status

Current test environment health:

```
TEST ENVIRONMENT:

📁 Test Workspace (test_workspace/)
   Status:      ✅ HEALTHY
   Files:       6 test files
   Total Size:  1.2 MB
   Last Update: 2 hours ago

🔧 Test Scripts
   run_automated_tests.py:  ✅ Functional
   Python Version:          3.11.x
   Dependencies:            All satisfied

📊 Test Data
   automated_test_results.json:  ✅ Current
   agent_debug.log:              ✅ Available
   Last backup:                   1 day ago
```

### 6. Pass/Fail Statistics

Historical and current statistics:

```
STATISTICS:

Current Run:
   Total:      20 tests
   Passed:     20 (100%)
   Failed:     0 (0%)
   Skipped:    0 (0%)
   Duration:   2.1 seconds

Last 10 Runs:
   Average Pass Rate:  100%
   Flaky Tests:        0
   Total Executions:   200 tests
   Total Failures:     0

Trend: ✅ STABLE
```

### 7. Coverage Metrics

Test coverage analysis:

```
COVERAGE ANALYSIS:

Operations Tested:
   ✅ FILE_READ:      100% (all scenarios)
   ✅ FILE_WRITE:     100% (all scenarios)
   ✅ FILE_EDIT:      100% (all scenarios)
   ❌ FILE_DELETE:    0% (not implemented)
   ❌ FILE_RENAME:    0% (not implemented)
   ❌ FILE_COPY:      0% (not implemented)

Security Coverage:
   ✅ Path Traversal:     Tested
   ✅ Directory Control:  Tested
   ✅ Size Limits:        Tested
   ✅ Permissions:        Tested
   ✅ Path Resolution:    Tested

Feature Coverage:
   ✅ Core Operations:    100%
   ⚠️  Error Handling:    70%
   ⚠️  Edge Cases:        80%
   ❌ Advanced Features:  0% (not impl.)

Overall Coverage: 85%
```

### 8. Health Score

Calculate testing health score (0-100):

```
HEALTH SCORE: 95/100

Breakdown:
✅ All Tests Passing:         +30 points
✅ Security Tests Passing:    +20 points
✅ Recent Execution (<1 day): +15 points
✅ Good Coverage (>80%):      +15 points
✅ Fast Execution (<5s):      +10 points
⚠️  Some Gaps in Coverage:    -5 points

Health Rating: EXCELLENT ✅
```

### 9. Priority Actions

What needs attention:

```
ACTION ITEMS:

🔴 HIGH PRIORITY:
   - None

🟡 MEDIUM PRIORITY:
   1. Add FILE_DELETE operation tests (when implemented)
   2. Expand error handling test coverage
   3. Add concurrent operation tests

🟢 LOW PRIORITY:
   1. Archive old test results
   2. Add performance benchmarking
   3. Create automated regression tracking
```

### 10. Recommendations

Based on current status:

```
RECOMMENDATIONS:

Immediate Actions:
   ✅ No immediate actions required
   System is healthy and stable

Maintenance Tasks:
   📅 Weekly: Run full test suite
   📅 Monthly: Review and update test plan
   📅 Quarterly: Comprehensive coverage analysis

Improvements:
   💡 Consider adding FILE_DELETE/RENAME/COPY when ready
   💡 Implement automated test scheduling
   💡 Add performance regression tests
```

## Commands to Gather Status

```bash
# Check last test run
ls -lt automated_test_results.json

# View test results
cat automated_test_results.json | python -m json.tool

# Check test workspace
ls -lh test_workspace/

# View recent logs
tail -50 agent_debug.log

# Check test file ages
find test_workspace/ -type f -ls
```

## Status Indicators

### Health Indicators
- 🟢 **Excellent** (95-100): All tests passing, recent execution, good coverage
- 🟡 **Good** (80-94): Most tests passing, acceptable coverage
- 🟠 **Fair** (60-79): Some failures or gaps, needs attention
- 🔴 **Poor** (<60): Significant issues, immediate action required

### Test Status Icons
- ✅ **PASSING**: Test consistently passes
- ❌ **FAILING**: Test consistently fails
- ⚠️ **FLAKY**: Test intermittently fails
- ⏭️ **SKIPPED**: Test intentionally skipped
- 🚫 **DISABLED**: Test temporarily disabled
- 📋 **PENDING**: Test documented but not implemented

## Quick Commands

Provide shortcuts for common queries:

```
QUICK STATUS COMMANDS:

/test-status quick     # Quick overview only
/test-status full      # Complete dashboard (default)
/test-status coverage  # Coverage analysis only
/test-status health    # Health score only
/test-status recent    # Recent activity only
```

## Alert Conditions

**Automatically alert when:**

- 🚨 **Critical**: Any test failures
- 🚨 **Critical**: Security test failures
- ⚠️ **Warning**: Pass rate <95%
- ⚠️ **Warning**: Tests haven't run in >1 week
- ⚠️ **Warning**: Health score <80
- 📊 **Info**: Coverage below target (85%)

## Comparison View

Compare current status to targets:

```
STATUS vs TARGETS:

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Pass Rate | 100% | 100% | ✅ Met |
| Coverage | 85% | 90% | ⚠️ Below |
| Health Score | 95 | 90 | ✅ Exceeded |
| Execution Time | 2.1s | <5s | ✅ Met |
| Last Run | 2h ago | <24h | ✅ Met |
```

## Coordination

### Share Status With Documentation Subagent

When significant changes occur:
```
TEST SUBAGENT → DOCUMENTATION SUBAGENT

STATUS UPDATE:
- Test health dropped to 75 (was 95)
- New test failures detected
- Coverage gap identified

ACTION REQUIRED:
- Update TESTING_SUMMARY.md with current status
- Add failure details to test_results.md
- Regenerate HTML pages

DATA:
- Current health score: 75
- Failed tests: 2
- Recommendations: [list]
```

### Escalate to User

**Immediate escalation when:**
- Any test failure
- Security vulnerability detected
- Health score <70
- Critical issues found

**Scheduled reporting:**
- Daily status summary (if requested)
- Weekly trend analysis
- Monthly comprehensive review

## Status Persistence

**Save status for trending:**

```bash
# Append to status history
echo "$(date '+%Y-%m-%d %H:%M:%S'),95,100%,2.1s" >> test_status_history.csv
```

**Track over time:**
- Health score trending
- Pass rate trending
- Execution time trending
- Coverage trending

---

**Remember:** Status is a snapshot. Use it to detect changes and trends, not just current state.
