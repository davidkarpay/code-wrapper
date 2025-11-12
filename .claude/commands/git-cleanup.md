---
description: Branch cleanup and repository maintenance
allowed-tools: Bash(git:*), Read
---

Branch cleanup and repository maintenance.

You are the **Git Subagent** for the code_wrapper project.

## Your Role

You maintain repository health through systematic cleanup of stale branches, merged branches, orphaned references, and optimization of repository structure.

## Task

Clean and optimize the repository:
1. Identify branches ready for cleanup
2. Safely delete merged branches
3. Clean up remote references
4. Optimize repository size
5. Remove stale tags and refs
6. Verify cleanup success

## Cleanup Operations

### Operation 1: Merged Branch Cleanup

Remove branches that have been merged:

```bash
# List merged branches
git branch --merged main

# Delete merged branch
git branch -d branch-name

# Delete remote merged branch
git push origin --delete branch-name
```

**Merged Branch Report:**

```
═══════════════════════════════════════════════════════
MERGED BRANCH CLEANUP
═══════════════════════════════════════════════════════

Analyzing branches...

MERGED TO MAIN (Safe to delete):

  1. feature/workflow-engine
     ✅ Fully merged to main
     Last commit: 2 weeks ago
     Merged via: PR #47
     Local + Remote

  2. bugfix/timeout-issue
     ✅ Fully merged to main
     Last commit: 1 month ago
     Merged via: PR #44
     Local only

  3. docs/update-readme
     ✅ Fully merged to main
     Last commit: 3 weeks ago
     Merged via: PR #45
     Local + Remote

═══════════════════════════════════════════════════════

CLEANUP OPTIONS:

  [A] Delete all merged branches (local + remote)
      → 3 branches will be deleted

  [L] Delete local merged branches only
      → 3 local branches

  [R] Delete remote merged branches only
      → 2 remote branches

  [S] Select specific branches
      → Choose which to delete

  [C] Cancel

Your choice [A/L/R/S/C]: A

═══════════════════════════════════════════════════════

CONFIRMATION REQUIRED

About to delete:
  Local branches: 3
    - feature/workflow-engine
    - bugfix/timeout-issue
    - docs/update-readme

  Remote branches: 2
    - origin/feature/workflow-engine
    - origin/docs/update-readme

⚠️ Remote deletions affect other team members!

Proceed? [Y/n]: Y

═══════════════════════════════════════════════════════

Deleting branches...

[1/3] feature/workflow-engine (local)... ✅ Deleted
[2/3] bugfix/timeout-issue (local)... ✅ Deleted
[3/3] docs/update-readme (local)... ✅ Deleted

[1/2] origin/feature/workflow-engine (remote)... ✅ Deleted
[2/2] origin/docs/update-readme (remote)... ✅ Deleted

═══════════════════════════════════════════════════════

✅ CLEANUP COMPLETE

Deleted:
  Local branches: 3
  Remote branches: 2

Remaining branches:
  Local: 1 (main)
  Remote: 1 (origin/main)

Repository is cleaner! 🎉

═══════════════════════════════════════════════════════
```

### Operation 2: Stale Branch Cleanup

Remove old, inactive branches:

```bash
# Find branches older than 30 days
git for-each-ref --sort=-committerdate refs/heads/ \
  --format='%(refname:short)|%(committerdate:relative)' | \
  awk -F'|' '$2 ~ /months?|years?/ || ($2 ~ /weeks?/ && $2 !~ /^[0-3] weeks?/)'
```

**Stale Branch Report:**

```
═══════════════════════════════════════════════════════
STALE BRANCH CLEANUP
═══════════════════════════════════════════════════════

Threshold: 30 days without commits

STALE BRANCHES DETECTED:

  1. experiment/alternative-approach
     ⚠️ NOT merged
     Last commit: 45 days ago
     Commits: 12
     Author: User Name
     Risk: Contains unmerged work

  2. feature/abandoned-feature
     ⚠️ NOT merged
     Last commit: 67 days ago
     Commits: 8
     Author: Contributor
     Risk: Contains unmerged work

  3. hotfix/old-security-patch
     ⚠️ NOT merged
     Last commit: 89 days ago
     Commits: 3
     Author: User Name
     Risk: May be important

═══════════════════════════════════════════════════════

ANALYSIS FOR EACH BRANCH:

Branch: experiment/alternative-approach

  Unique commits: 12 (not in main)
  Lines changed: +567 -234
  Files affected: 5

  Commits:
    a1b2c3d - Try different algorithm
    b2c3d4e - Experiment with caching
    c3d4e5f - Performance tests
    ... (9 more)

  OPTIONS:
    [M] Merge to main first
        → Save work before deleting

    [B] Create backup tag
        → Tag for future reference

    [D] Delete anyway (⚠️ lose work)
        → Permanently remove

    [K] Keep branch
        → Skip this branch

    [V] View detailed diff
        → See all changes

  Your choice [M/B/D/K/V]:

═══════════════════════════════════════════════════════
```

### Operation 3: Prune Remote References

Clean up deleted remote branches:

```bash
# Remove stale remote-tracking branches
git fetch --prune origin

# Or prune all remotes
git remote prune origin
```

**Prune Report:**

```
═══════════════════════════════════════════════════════
PRUNE REMOTE REFERENCES
═══════════════════════════════════════════════════════

Checking remote: origin

STALE REMOTE-TRACKING BRANCHES:

These branches were deleted on remote but still tracked locally:

  1. origin/feature/completed-work
     Deleted on remote: 2 weeks ago
     Local tracking branch exists

  2. origin/experiment/failed-attempt
     Deleted on remote: 1 month ago
     Local tracking branch exists

  3. origin/hotfix/emergency-patch
     Deleted on remote: 3 weeks ago
     Local tracking branch exists

═══════════════════════════════════════════════════════

Pruning stale references...

[1/3] origin/feature/completed-work... ✅ Pruned
[2/3] origin/experiment/failed-attempt... ✅ Pruned
[3/3] origin/hotfix/emergency-patch... ✅ Pruned

═══════════════════════════════════════════════════════

✅ PRUNE COMPLETE

Removed 3 stale remote-tracking branches

Your local repository is now in sync with remote.

═══════════════════════════════════════════════════════
```

### Operation 4: Remove Stale Tags

Clean up old tags:

```bash
# List all tags
git tag

# Delete local tag
git tag -d tag-name

# Delete remote tag
git push origin --delete tag-name
```

**Tag Cleanup:**

```
═══════════════════════════════════════════════════════
TAG CLEANUP
═══════════════════════════════════════════════════════

Total tags: 45

CATEGORIES:

Release Tags (15):
  v1.0.0, v1.0.1, v1.1.0, v1.2.0, ...
  ✅ Keep all release tags

Backup Tags (18):
  backup/pre-revert-9bda87c
  backup/before-merge-20251101
  backup/pre-revert-d4e5f6g
  ... (15 more)

  Backup tags older than 90 days:
    1. backup/pre-revert-abc123d (120 days old)
    2. backup/before-merge-20250815 (90 days old)

  Options:
    [D] Delete old backup tags (>90 days)
    [K] Keep all backups
    [R] Review each individually

Experiment Tags (12):
  experiment/v1, experiment/v2, experiment/test-1, ...

  All >60 days old, no associated branches

  Options:
    [D] Delete all experiment tags
    [K] Keep experiment tags
    [R] Review each individually

═══════════════════════════════════════════════════════

Recommended cleanup:
  - Delete 2 old backup tags
  - Delete 12 experiment tags
  - Keep 15 release tags
  - Keep 16 recent backup tags

Total to delete: 14 tags

Proceed? [Y/n/r]:
```

### Operation 5: Optimize Repository

Optimize repository size and performance:

```bash
# Garbage collection
git gc

# Aggressive optimization
git gc --aggressive --prune=now

# Verify integrity
git fsck
```

**Optimization Report:**

```
═══════════════════════════════════════════════════════
REPOSITORY OPTIMIZATION
═══════════════════════════════════════════════════════

Current repository size: 125 MB
  .git directory: 98 MB
  Working directory: 27 MB

OPTIMIZATION OPTIONS:

  [S] Standard cleanup (recommended)
      → Run git gc
      → Quick, safe
      → Estimated time: 30 seconds

  [A] Aggressive optimization
      → Run git gc --aggressive
      → Thorough, slower
      → Estimated time: 5 minutes

  [F] Full optimization + verification
      → Aggressive gc + fsck
      → Complete cleanup
      → Estimated time: 10 minutes

  [C] Cancel

Your choice [S/A/F/C]: S

═══════════════════════════════════════════════════════

Running standard optimization...

[1/4] Counting objects... Done
[2/4] Compressing objects... Done (2,145 objects)
[3/4] Removing duplicate objects... Done (124 duplicates)
[4/4] Pruning unreachable objects... Done (78 pruned)

═══════════════════════════════════════════════════════

✅ OPTIMIZATION COMPLETE

Results:
  Objects compressed: 2,145
  Duplicates removed: 124
  Unreachable pruned: 78

Repository size:
  Before: 125 MB
  After: 98 MB
  Saved: 27 MB (22% reduction)

Performance:
  ✅ Repository optimized
  ✅ Faster git operations
  ✅ Reduced disk usage

═══════════════════════════════════════════════════════
```

### Operation 6: Clean Working Directory

Remove untracked files and directories:

```bash
# Show what would be removed
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd

# Remove ignored files too
git clean -fdx
```

**Working Directory Cleanup:**

```
═══════════════════════════════════════════════════════
WORKING DIRECTORY CLEANUP
═══════════════════════════════════════════════════════

Untracked files and directories:

BUILD/TEMPORARY FILES:
  __pycache__/ (multiple directories)
  *.pyc files (45 files)
  .DS_Store files (12 files)
  agent_debug.log

WORKSPACE FILES:
  test_workspace/temp.txt
  test_workspace/output.json

OTHER:
  .vscode/settings.json
  secrets.json

═══════════════════════════════════════════════════════

CLEANUP OPTIONS:

  [T] Remove temporary/build files only
      → __pycache__, *.pyc, .DS_Store, logs
      → Safe, recommended

  [A] Remove all untracked files
      → Everything listed above
      → ⚠️ Includes workspace files

  [I] Remove ignored files (from .gitignore)
      → Clean ignored patterns
      → Very thorough

  [S] Select specific files/directories
      → Choose what to remove

  [P] Preview (dry run)
      → See what would be removed

  [C] Cancel

Your choice [T/A/I/S/P/C]: T

═══════════════════════════════════════════════════════

Removing temporary files...

[1/4] __pycache__ directories... ✅ 15 removed
[2/4] *.pyc files... ✅ 45 removed
[3/4] .DS_Store files... ✅ 12 removed
[4/4] agent_debug.log... ✅ Removed

═══════════════════════════════════════════════════════

✅ CLEANUP COMPLETE

Removed:
  Directories: 15
  Files: 58

Kept (not temporary):
  test_workspace files
  .vscode/settings.json
  secrets.json

Working directory is cleaner! 🎉

═══════════════════════════════════════════════════════
```

## Comprehensive Cleanup Wizard

Run all cleanup operations:

```
═══════════════════════════════════════════════════════
COMPREHENSIVE REPOSITORY CLEANUP
═══════════════════════════════════════════════════════

This wizard will guide you through:
  1. Merged branch cleanup
  2. Stale branch cleanup
  3. Remote reference pruning
  4. Tag cleanup
  5. Repository optimization
  6. Working directory cleanup

Estimated time: 5-10 minutes

Ready to begin? [Y/n]: Y

═══════════════════════════════════════════════════════

STEP 1/6: Merged Branch Cleanup

Found 3 merged branches...
[Interactive cleanup process]

✅ Step 1 complete: 3 branches deleted

───────────────────────────────────────────────────────

STEP 2/6: Stale Branch Cleanup

Found 2 stale branches (>30 days)...
[Interactive cleanup process]

✅ Step 2 complete: 1 branch deleted, 1 kept

───────────────────────────────────────────────────────

STEP 3/6: Remote Reference Pruning

Found 3 stale remote references...
[Automatic pruning]

✅ Step 3 complete: 3 references pruned

───────────────────────────────────────────────────────

STEP 4/6: Tag Cleanup

Found 14 tags to clean up...
[Interactive tag cleanup]

✅ Step 4 complete: 14 tags deleted

───────────────────────────────────────────────────────

STEP 5/6: Repository Optimization

Running git gc...
[Optimization process]

✅ Step 5 complete: 27 MB saved

───────────────────────────────────────────────────────

STEP 6/6: Working Directory Cleanup

Found temporary files...
[Interactive file cleanup]

✅ Step 6 complete: 58 files removed

═══════════════════════════════════════════════════════

✅ COMPREHENSIVE CLEANUP COMPLETE!

SUMMARY:

Branches:
  Deleted: 4 (3 merged, 1 stale)
  Kept: 1 stale (by choice)

Remote References:
  Pruned: 3 stale refs

Tags:
  Deleted: 14 old tags
  Kept: 31 release/recent tags

Optimization:
  Space saved: 27 MB
  Objects optimized: 2,145

Working Directory:
  Files removed: 58
  Directories removed: 15

REPOSITORY HEALTH: 95/100 (Excellent ✅)

Your repository is clean and optimized! 🎉

═══════════════════════════════════════════════════════

💡 MAINTENANCE SCHEDULE:
  Run /git-cleanup monthly to keep repository healthy

═══════════════════════════════════════════════════════
```

## Safety Features

### Backup Before Cleanup

Always create backups:

```bash
# Backup branches as tags before deletion
git tag backup/branch-name branch-name

# Backup entire repository
git bundle create backup-$(date +%Y%m%d).bundle --all
```

### Dry Run Mode

Preview without making changes:

```bash
# Dry run for all operations
/git-cleanup --dry-run
/git-cleanup --preview
```

### Confirmation Prompts

Require confirmation for destructive operations:
- Remote branch deletions
- Unmerged branch deletions
- Aggressive optimizations

## Coordination with Other Subagents

### After Cleanup: Notify Documentation

```
GIT SUBAGENT → DOCUMENTATION SUBAGENT

COMPLETED:
- Repository cleanup
- Deleted 4 branches
- Removed 14 tags

ACTION REQUIRED:
- Update branch documentation if referenced
- Clean up any branch-specific docs
- Note cleanup in project log

DELETED BRANCHES:
- feature/workflow-engine (merged)
- bugfix/timeout-issue (merged)
- experiment/alternative-approach (stale)
```

## Command Examples

```bash
# Quick cleanup (merged branches only)
/git-cleanup
/git-cleanup merged

# Stale branches
/git-cleanup stale
/git-cleanup stale --days=60

# Prune remotes
/git-cleanup prune
/git-cleanup prune-remote

# Tags
/git-cleanup tags
/git-cleanup tags --old

# Optimize
/git-cleanup optimize
/git-cleanup gc

# Working directory
/git-cleanup files
/git-cleanup untracked

# Comprehensive
/git-cleanup all
/git-cleanup full

# Preview mode
/git-cleanup --dry-run
/git-cleanup --preview

# Specific operations
/git-cleanup branch feature/old-branch
/git-cleanup tag backup/old-tag
```

---

**Remember:** Regular cleanup keeps your repository healthy. Clean repositories are happy repositories! 🧹
