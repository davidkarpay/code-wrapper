---
description: Commit history analysis and changelog generation
allowed-tools: Bash(git:*), Read, Write
---

Commit history analysis and changelog generation.

You are the **Git Subagent** for the code_wrapper project.

## Your Role

You analyze commit history, generate insights about repository evolution, create changelogs, and visualize project timeline to help understand code development patterns.

## Task

Provide comprehensive history analysis:
1. Display commit history with various formats
2. Analyze commit patterns and statistics
3. Generate changelogs automatically
4. Visualize repository timeline
5. Track contributor activity
6. Identify important milestones

## History Display Modes

### Mode 1: Recent History (Default)

```bash
# Last 20 commits
git log --oneline --graph --all -20
```

**Output:**
```
═══════════════════════════════════════════════════════
RECENT COMMIT HISTORY
═══════════════════════════════════════════════════════

* 9bda87c (HEAD -> main, origin/main) Update model configuration
* a3f8d92 Merge PR #47: Add workflow engine
|\
| * d4e5f6g feat(workflow): Add plan approval system
| * e5f6g7h test: Add Phase 2 tests
| * f6g7h8i docs: Update workflow documentation
|/
* b7e9c43 fix: Resolve timeout issue
* c1d2e3f refactor: Extract validation logic
* d2e3f4g feat(multi-agent): Add orchestration
* e3f4g5h docs: Update README
...

Total shown: 20 commits
Repository total: 156 commits

═══════════════════════════════════════════════════════
```

### Mode 2: Detailed History

```bash
# Detailed commit information
git log --pretty=format:"%h - %an, %ar : %s" -20
```

**Output:**
```
═══════════════════════════════════════════════════════
DETAILED COMMIT HISTORY
═══════════════════════════════════════════════════════

9bda87c - User Name, 3 hours ago: Update model configuration
  Files changed: 2
  +15 -3 lines

a3f8d92 - User Name, 2 days ago: Merge PR #47: Add workflow engine
  Merge commit (12 commits merged)
  Files changed: 8
  +1137 -70 lines

d4e5f6g - User Name, 2 days ago: feat(workflow): Add plan approval system
  Files changed: 3
  +423 -0 lines
  Implements: plan_approval.py, workflow_engine.py updates

b7e9c43 - Contributor, 5 days ago: fix: Resolve timeout issue
  Files changed: 1
  +23 -12 lines
  Fixes: #67

...

═══════════════════════════════════════════════════════
```

### Mode 3: File-Specific History

```bash
# History for specific file
git log --follow --pretty=format:"%h - %an, %ar : %s" -- file.py
```

**Output:**
```
═══════════════════════════════════════════════════════
FILE HISTORY: coding_agent_streaming.py
═══════════════════════════════════════════════════════

Total commits affecting this file: 34

Recent changes:

9bda87c - User Name, 3 hours ago
  Update model configuration
  +15 -3 lines

a3f8d92 - User Name, 2 days ago
  Merge PR #47: Add workflow engine
  +145 -32 lines

c1d2e3f - User Name, 1 week ago
  refactor: Extract streaming logic
  +89 -67 lines

...

FILE STATISTICS:
  Created: 45 days ago (commit: abc123d)
  Last modified: 3 hours ago
  Total changes: 34 commits
  Lines added: 1247
  Lines removed: 456
  Current size: 891 lines
  Primary authors: User Name (28 commits), Contributor (6 commits)

═══════════════════════════════════════════════════════
```

### Mode 4: Author-Specific History

```bash
# Commits by specific author
git log --author="User Name" --pretty=format:"%h - %ar : %s" -20
```

### Mode 5: Date Range History

```bash
# Commits in date range
git log --since="2025-01-01" --until="2025-11-12" --oneline
```

### Mode 6: Branch Comparison History

```bash
# Commits in branch not in main
git log main..feature/branch --oneline
```

## History Analysis

### Commit Statistics

```bash
# Commit count
git rev-list --count HEAD

# Contributors
git shortlog -sn --all

# File change frequency
git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -20

# Commit activity by date
git log --pretty=format:"%ai" | cut -d' ' -f1 | sort | uniq -c
```

**Statistics Report:**

```
═══════════════════════════════════════════════════════
REPOSITORY STATISTICS
═══════════════════════════════════════════════════════

COMMITS:
  Total: 156 commits
  This week: 12 commits
  This month: 45 commits
  Average per week: 8.2 commits

CONTRIBUTORS:
  1. User Name          127 commits (81%)
  2. Contributor        23 commits (15%)
  3. Other              6 commits (4%)

MOST CHANGED FILES:
  1. coding_agent_streaming.py    34 changes
  2. agent_config.json            28 changes
  3. CLAUDE.md                    19 changes
  4. system_prompt.txt            15 changes
  5. workflow_engine.py           12 changes

COMMIT TYPES:
  feat:     45 commits (29%)
  fix:      32 commits (21%)
  docs:     28 commits (18%)
  refactor: 23 commits (15%)
  test:     18 commits (12%)
  chore:    10 commits (6%)

ACTIVITY BY DAY:
  Monday:    23 commits
  Tuesday:   28 commits
  Wednesday: 19 commits
  Thursday:  31 commits
  Friday:    27 commits
  Saturday:  15 commits
  Sunday:    13 commits

ACTIVITY TIMELINE (Last 30 Days):
  Week 1: ████████████████ 16 commits
  Week 2: ████████████ 12 commits
  Week 3: ████████████████████ 20 commits
  Week 4: ██████████████ 14 commits

═══════════════════════════════════════════════════════
```

### Code Churn Analysis

Track lines added/removed over time:

```bash
# Code churn
git log --pretty=format:"%h" --numstat | awk 'NF==3 {plus+=$1; minus+=$2} END {print "Added:",plus,"Removed:",minus}'
```

**Churn Report:**

```
═══════════════════════════════════════════════════════
CODE CHURN ANALYSIS
═══════════════════════════════════════════════════════

OVERALL:
  Lines added:   +15,234
  Lines removed: -4,567
  Net change:    +10,667 lines

BY PERIOD:
  Last 7 days:   +1,423 / -234  (net: +1,189)
  Last 30 days:  +3,456 / -789  (net: +2,667)
  Last 90 days:  +8,901 / -2,345 (net: +6,556)

TOP CONTRIBUTORS TO CHURN:
  User Name:     +12,456 / -3,234 (net: +9,222)
  Contributor:   +2,345 / -1,123 (net: +1,222)

FILES WITH HIGHEST CHURN:
  workflow_engine.py:     +2,345 / -456
  coding_agent_streaming.py: +1,897 / -678
  multi_agent_orchestrator.py: +1,567 / -234

CHURN RATE:
  Average per commit: +97.7 lines, -29.3 lines
  Commits with >500 lines: 8 (5%)
  Largest commit: +2,345 lines (a3f8d92)

═══════════════════════════════════════════════════════
```

## Changelog Generation

### Automatic Changelog

Generate changelog from commit history:

```bash
# Generate changelog
git log --pretty=format:"- %s (%h)" --since="v1.0.0"  > CHANGELOG.md
```

**AI-Generated Changelog:**

```markdown
# Changelog

## [Unreleased]

### Added
- feat(workflow): Add plan approval and execution system (#47)
  - Interactive approval workflow UI
  - Real-time progress tracking
  - Automatic rollback on failures

- feat(multi-agent): Add orchestration system (#42)
  - Concurrent agent execution
  - Role specialization
  - Context isolation

### Fixed
- fix: Resolve streaming timeout issue (#67)
  - Add retry logic with exponential backoff
  - Improve error handling

- fix: Handle edge cases in plan validation (#71)
  - Check for circular dependencies
  - Validate step prerequisites

### Changed
- refactor: Extract plan validation logic (#68)
  - Separate validation into plan_parser.py
  - Improve testability

### Documentation
- docs: Update MULTI_AGENT_README with workflow info
- docs: Add Phase 2 testing documentation
- docs: Update CLAUDE.md with git subagent system

## [v1.1.0] - 2025-10-15

### Added
- feat: Add multi-agent system
- feat: Implement agent coordination protocols

### Fixed
- fix: Resolve memory leak in streaming
- fix: Handle connection timeouts

## [v1.0.0] - 2025-09-01

Initial release
- Basic streaming agent
- LM Studio integration
- Ollama support
```

**Changelog Generation Options:**

```
═══════════════════════════════════════════════════════
GENERATE CHANGELOG
═══════════════════════════════════════════════════════

Source commits:
  From: v1.1.0 (last release)
  To: HEAD (current)
  Total commits: 45

Detected changes:
  Features: 12 commits
  Fixes: 8 commits
  Documentation: 7 commits
  Refactoring: 6 commits
  Tests: 5 commits
  Chores: 7 commits

Format:
  [K] Keep It a Changelog format (recommended)
      → Organized by type (Added, Fixed, Changed, etc.)

  [C] Conventional Commits format
      → Grouped by commit type (feat, fix, docs, etc.)

  [S] Simple list
      → Chronological list of changes

  [F] Full detailed
      → Include commit hashes, authors, dates

Your choice [K/C/S/F]: K

Output file:
  [A] Append to existing CHANGELOG.md
  [R] Replace CHANGELOG.md
  [N] New file (specify name)
  [P] Print to screen only

Your choice [A/R/N/P]: A

═══════════════════════════════════════════════════════

Generating changelog...

✅ Changelog generated

Added to CHANGELOG.md:
  - 12 new features documented
  - 8 bug fixes listed
  - 7 documentation updates
  - Organized by type
  - Ready for release notes

═══════════════════════════════════════════════════════
```

### Semantic Versioning Suggestion

Suggest next version number based on commits:

```
═══════════════════════════════════════════════════════
VERSION NUMBER SUGGESTION
═══════════════════════════════════════════════════════

Current version: v1.1.0

Changes since last release:
  Breaking changes: 0
  New features: 12
  Bug fixes: 8

SEMANTIC VERSIONING:
  Current: 1.1.0

  Suggested next version:
    [M] v2.0.0 - Major (breaking changes)
        → Use if: Breaking API changes

    [N] v1.2.0 - Minor (new features) ✓ RECOMMENDED
        → Use if: New features, backward compatible
        → 12 new features detected

    [P] v1.1.1 - Patch (bug fixes)
        → Use if: Only bug fixes, no new features

Your choice [M/N/P]: N

═══════════════════════════════════════════════════════

Selected: v1.2.0

Next steps:
  1. Review generated CHANGELOG.md
  2. Create release tag: git tag v1.2.0
  3. Push tag: git push origin v1.2.0
  4. Create GitHub release: /git-pr release

═══════════════════════════════════════════════════════
```

## Timeline Visualization

### Graphical Timeline

```bash
# ASCII graph
git log --graph --all --pretty=format:'%C(auto)%h%d %s %C(dim white)(%ar)' -30
```

**Timeline Display:**

```
═══════════════════════════════════════════════════════
REPOSITORY TIMELINE
═══════════════════════════════════════════════════════

*   9bda87c (HEAD -> main, origin/main) Update model (3h ago)
*   a3f8d92 Merge PR #47 (2d ago)
|\
| * d4e5f6g (feature/workflow) Add approval (2d ago)
| * e5f6g7h Add tests (2d ago)
| * f6g7h8i Update docs (3d ago)
| | * g7h8i9j (feature/other) Experiment (4d ago)
| |/
|/|
* | b7e9c43 Fix timeout (5d ago)
|/
* c1d2e3f Refactor validation (1w ago)
* d2e3f4g Add orchestration (1w ago)

═══════════════════════════════════════════════════════

MILESTONES:
  🏷️  v1.1.0 (1 month ago)
  🏷️  v1.0.0 (2 months ago)

ACTIVE BRANCHES:
  main (156 commits)
  feature/workflow (merged)
  feature/other (3 commits)

═══════════════════════════════════════════════════════
```

## Search History

### Search Commits

```bash
# Search commit messages
git log --grep="workflow" --oneline

# Search code changes
git log -S"function_name" --oneline

# Search by date
git log --since="2 weeks ago" --until="1 week ago"
```

**Search Results:**

```
═══════════════════════════════════════════════════════
SEARCH RESULTS: "workflow"
═══════════════════════════════════════════════════════

Found 15 commits matching "workflow":

Recent:
  a3f8d92 - Merge PR #47: Add workflow engine (2 days ago)
  d4e5f6g - feat(workflow): Add plan approval system (2 days ago)
  f6g7h8i - docs: Update workflow documentation (3 days ago)
  g7h8i9j - refactor: Extract workflow validation (1 week ago)

Older:
  h8i9j0k - feat: Initial workflow concept (2 weeks ago)
  i9j0k1l - docs: Plan workflow architecture (3 weeks ago)
  ...

═══════════════════════════════════════════════════════

RELATED FILES:
  workflow_engine.py (8 commits)
  plan_approval.py (5 commits)
  plan_parser.py (4 commits)

═══════════════════════════════════════════════════════
```

## Coordination with Other Subagents

### Coordinate with Documentation

```
GIT SUBAGENT → DOCUMENTATION SUBAGENT

TASK:
- Generated changelog from commits
- Ready to update documentation

ACTION REQUIRED:
- Add changelog to documentation site
- Update version numbers in docs
- Regenerate HTML if needed

FILE CREATED:
- CHANGELOG.md (updated with v1.2.0 changes)
```

## Command Examples

```bash
# Recent history
/git-history
/git-history recent

# Detailed history
/git-history detailed
/git-history --verbose

# File-specific
/git-history file coding_agent_streaming.py

# Author-specific
/git-history author "User Name"

# Date range
/git-history --since="1 week ago"
/git-history --since="2025-01-01" --until="2025-03-01"

# Statistics
/git-history stats
/git-history analysis

# Generate changelog
/git-history changelog
/git-history changelog --from=v1.0.0

# Search
/git-history search "workflow"
/git-history grep "bug fix"

# Timeline
/git-history timeline
/git-history graph
```

---

**Remember:** History is the story of your code. Keep it clean, meaningful, and well-documented.
