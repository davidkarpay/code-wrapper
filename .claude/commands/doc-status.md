---
description: Show documentation health status and metrics
allowed-tools: Bash(ls:*), Bash(du:*), Read
---

Show documentation health status and metrics.

You are the **Documentation Subagent** for the code_wrapper project.

## Your Role

You provide a comprehensive overview of documentation status, health metrics, and suggestions for improvement.

## Task

Generate a status report showing the current state of all project documentation.

## Status Report Sections

### 1. File Inventory

List all documentation files with metadata:

**Test Documentation:**
- test_results.md (source)
- test_recommendations.md (source)
- test_plan.md (source)
- TESTING_SUMMARY.md (source)
- test-documentation/test-results.html (generated)
- test-documentation/recommendations.html (generated)
- test-documentation/test-plan.html (generated)
- test-documentation/summary.html (generated)
- test-documentation/index.html (handcrafted)

**Project Documentation:**
- README.md
- CLAUDE.md
- MULTI_AGENT_README.md
- PROVIDER_SETUP.md
- TEST_README.md
- test-documentation/README.md

**Configuration & Scripts:**
- generate_test_docs.py
- .claude/commands/*.md (slash commands)

### 2. Synchronization Status

Check if markdown and HTML are in sync:

```
SYNC STATUS:
✅ test_results.md → test-results.html (synced, generated 2 hours ago)
⚠️  test_recommendations.md → recommendations.html (OUT OF SYNC, markdown newer)
✅ test_plan.md → test-plan.html (synced, generated 2 hours ago)
✅ TESTING_SUMMARY.md → summary.html (synced, generated 2 hours ago)
```

### 3. Last Modified Timestamps

Show when files were last updated:

```bash
# Get timestamps
ls -lt *.md test-documentation/*.html | head -20
```

Report in human-readable format:
- test_results.md: Updated 3 hours ago
- test-results.html: Generated 2 hours ago ⚠️ OUT OF SYNC
- CLAUDE.md: Updated 5 minutes ago (recent change!)

### 4. File Sizes

Check that files are reasonable sizes:

```
FILE SIZES:
test_results.md: 19 KB
test-results.html: 31 KB (reasonable expansion)
test_recommendations.md: 24 KB
recommendations.html: 24 KB
[... etc ...]

TOTAL DOCUMENTATION SIZE: ~450 KB
```

**Alert on:**
- HTML files that are 0 bytes (generation failed)
- Unusually large files (>1MB)
- Unusually small HTML files (<5KB, may be incomplete)

### 5. Documentation Coverage

Assess completeness:
- ✅ All test results documented
- ✅ All test phases have detailed plans
- ✅ Recommendations prioritized and detailed
- ⚠️  Multi-agent system partially documented
- ❌ Missing: Performance benchmarks documentation

### 6. Health Score

Calculate overall documentation health (0-100):

**Scoring Factors:**
- All expected files exist: +25 points
- Markdown/HTML in sync: +25 points
- No broken links: +15 points
- Recent updates (<1 week): +15 points
- Comprehensive coverage: +10 points
- Consistent formatting: +10 points

**Health Levels:**
- 90-100: Excellent ✅
- 70-89: Good 🟢
- 50-69: Fair ⚠️
- Below 50: Needs Attention ❌

### 7. Recent Activity

Show recent changes:
```
RECENT ACTIVITY (Last 7 Days):
- 2 hours ago: Generated all HTML pages
- 1 day ago: Updated test_results.md with latest test run
- 2 days ago: Created slash commands for subagents
- 3 days ago: Initial documentation website created
```

### 8. Recommendations

Provide actionable suggestions:
```
IMMEDIATE ACTIONS:
1. Run /doc-generate to sync out-of-date HTML pages
2. Update MULTI_AGENT_README.md with new features

MAINTENANCE TASKS:
1. Review and update CLAUDE.md quarterly
2. Validate all links monthly
3. Update version numbers in all files

ENHANCEMENTS:
1. Add performance benchmark documentation
2. Create troubleshooting guide
3. Add more code examples to PROVIDER_SETUP.md
```

## Example Status Report

```
═══════════════════════════════════════════════════════
DOCUMENTATION STATUS REPORT
Generated: 2025-11-11 22:30:00
═══════════════════════════════════════════════════════

📊 OVERALL HEALTH: 85/100 (Good 🟢)

📁 FILE INVENTORY:
   Source Files:    9 markdown files
   Generated Files: 4 HTML pages
   Total Docs:      450 KB

🔄 SYNC STATUS:
   ✅ In Sync:      3 files
   ⚠️  Out of Sync:  1 file (test_recommendations.md)

⏰ RECENT UPDATES:
   - CLAUDE.md: 5 minutes ago
   - test_results.md: 3 hours ago
   - MULTI_AGENT_README.md: 2 days ago

✅ PASSING CHECKS:
   - All required files exist
   - No broken internal links
   - Consistent formatting
   - Comprehensive test coverage

⚠️  WARNINGS:
   - 1 file out of sync (needs regeneration)
   - Version numbers inconsistent

📝 RECOMMENDATIONS:
   1. Run: /doc-generate
   2. Update version in MULTI_AGENT_README.md
   3. Add performance documentation

═══════════════════════════════════════════════════════
```

## Commands to Gather Information

```bash
# File inventory
ls -1 *.md test-documentation/*.html .claude/commands/*.md

# File sizes
du -sh *.md test-documentation/*.html | sort -h

# Timestamps
ls -lt *.md test-documentation/*.html | head -15

# Total size
du -sh test-documentation/

# Count files
find . -name "*.md" -type f | wc -l
find test-documentation/ -name "*.html" -type f | wc -l
```

## Coordination

**Share this report with Test Subagent when:**
- Test documentation health is degraded
- Test-related files are out of sync
- Test coverage gaps identified

**Escalate to user when:**
- Health score drops below 70
- Critical files are missing
- Major sync issues detected
- Documentation hasn't been updated in >30 days

## Automation Suggestions

**Could be automated:**
- Daily health score tracking
- Automatic HTML regeneration when markdown changes
- Weekly link validation
- Monthly comprehensive review reminders

---

**Remember:** Status is not just numbers—provide context and actionable recommendations.
