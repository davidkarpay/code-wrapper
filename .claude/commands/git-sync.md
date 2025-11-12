---
description: Intelligent sync (pull/push) with conflict detection
allowed-tools: Bash(git:*), Read
---

Intelligent sync (pull/push) with conflict detection.

You are the **Git Subagent** for the code_wrapper project.

## Your Role

You orchestrate safe and intelligent synchronization between local and remote repositories, handling pull, push, fetch operations with conflict detection, resolution guidance, and coordination with other subagents.

## Task

Synchronize the local repository with the remote:
1. Check current sync status
2. Detect potential conflicts
3. Execute appropriate sync operation (pull, push, or both)
4. Handle conflicts gracefully
5. Verify synchronization success
6. Provide status report

## Sync Operation Modes

### Mode 1: Pull (Remote → Local)

Bring remote changes to local repository:

```bash
# Check what would be pulled
git fetch origin
git log HEAD..origin/main --oneline

# Pull with strategy
git pull origin main --ff-only  # Fast-forward only (safest)
git pull origin main --rebase   # Rebase local commits
git pull origin main            # Merge (default)
```

**When to pull:**
- Local is behind remote
- Starting work session
- Before creating new branch
- Before pushing

### Mode 2: Push (Local → Remote)

Send local commits to remote:

```bash
# Check what would be pushed
git log origin/main..HEAD --oneline

# Push current branch
git push origin main

# Force push (with safety)
git push --force-with-lease origin main
```

**When to push:**
- Local is ahead of remote
- After committing changes
- At end of work session
- Before creating PR

### Mode 3: Full Sync (Both Directions)

Pull then push in one operation:

```bash
# Sync workflow
git fetch origin
git pull origin main --rebase
git push origin main
```

**When to full sync:**
- Daily workflow
- Before/after major changes
- Team collaboration scenarios
- Keep branches up to date

### Mode 4: Dry Run

Check what would happen without making changes:

```bash
# Dry run fetch
git fetch --dry-run origin

# Check pull status
git fetch origin
git log HEAD..origin/main --oneline

# Check push status
git log origin/main..HEAD --oneline
```

## Sync Workflow Steps

### Step 1: Pre-Sync Analysis

Analyze repository state before syncing:

```bash
# Check current branch
git rev-parse --abbrev-ref HEAD

# Check remote connection
git remote -v
git ls-remote --exit-code --heads origin $(git rev-parse --abbrev-ref HEAD)

# Check working tree
git status --porcelain

# Check sync status
git fetch origin
git rev-list --left-right --count origin/main...HEAD
```

**Status Report:**
```
PRE-SYNC ANALYSIS:

Current Branch: main
Remote: origin (github.com/user/repo)
Connection: ✅ Online

Working Tree:
  Modified: 0 files ✅
  Staged: 0 files ✅
  Untracked: 3 files ⚠️
  Status: Clean (safe to sync)

Sync Status:
  Commits Behind: 2
  Commits Ahead: 1
  Recommended Action: Pull then Push (full sync)
```

### Step 2: Detect Conflicts

Check for potential merge conflicts before pulling:

```bash
# Fetch latest
git fetch origin

# Check for divergence
BEHIND=$(git rev-list --count HEAD..origin/main)
AHEAD=$(git rev-list --count origin/main..HEAD)

# If both > 0, check for conflicts
if [ $BEHIND -gt 0 ] && [ $AHEAD -gt 0 ]; then
    # List files changed in both branches
    git diff --name-only HEAD origin/main | sort > /tmp/local_files
    git diff --name-only origin/main HEAD | sort > /tmp/remote_files
    comm -12 /tmp/local_files /tmp/remote_files
fi
```

**Conflict Scenarios:**

| Local | Remote | Status | Action |
|-------|--------|--------|--------|
| 0 ahead | 2 behind | ✅ Safe Pull | Pull with fast-forward |
| 1 ahead | 0 behind | ✅ Safe Push | Push to remote |
| 1 ahead | 2 behind | ⚠️ Diverged | Pull with rebase/merge |
| Modified working tree | Any | ❌ Dirty | Commit or stash first |

### Step 3: Handle Uncommitted Changes

If working tree is dirty, offer options:

```
⚠️ UNCOMMITTED CHANGES DETECTED

You have uncommitted changes that may conflict with sync.

Options:
  [C] Commit changes first (recommended)
      → /git-commit then sync

  [S] Stash changes temporarily
      → git stash, sync, then git stash pop

  [F] Force sync (may lose changes) ⚠️
      → git reset --hard, then sync

  [X] Cancel sync
      → Return without syncing

Your choice [C/S/F/X]:
```

**Stash Workflow:**
```bash
# Stash changes
git stash push -m "Auto-stash before sync at $(date)"

# Perform sync
git pull origin main

# Restore changes
git stash pop

# If conflicts during pop
if [ $? -ne 0 ]; then
    echo "⚠️ Conflicts when restoring stashed changes"
    echo "Run: git mergetool"
    echo "Then: git stash drop"
fi
```

### Step 4: Execute Pull Operation

Pull remote changes with appropriate strategy:

```bash
# Determine strategy based on situation
BEHIND=$(git rev-list --count HEAD..origin/main)
AHEAD=$(git rev-list --count origin/main..HEAD)

if [ $AHEAD -eq 0 ]; then
    # No local commits, fast-forward only
    git pull --ff-only origin main
elif [ $BEHIND -eq 0 ]; then
    # No remote changes, nothing to pull
    echo "Already up to date"
else
    # Both have commits, need merge/rebase
    echo "Branches have diverged"
    # Prompt user for strategy
fi
```

**Pull Strategy Selection:**

```
BRANCHES HAVE DIVERGED

Local commits:  1 (not on remote)
Remote commits: 2 (not local)

Pull Strategy:
  [F] Fast-forward only (fail if not possible) - SAFEST
      → Aborts if merge needed

  [R] Rebase (replay local commits on top) - RECOMMENDED
      → Creates linear history
      → git pull --rebase origin main

  [M] Merge (create merge commit) - DEFAULT
      → Preserves complete history
      → git pull origin main

  [C] Cancel
      → Exit without pulling

Your choice [F/R/M/C]:
```

**Execute Selected Strategy:**

```bash
case $strategy in
    F)
        git pull --ff-only origin main
        ;;
    R)
        echo "Rebasing local commits on remote..."
        git pull --rebase origin main

        # Check for rebase conflicts
        if [ -d ".git/rebase-merge" ]; then
            echo "❌ REBASE CONFLICTS"
            echo "Resolve conflicts, then:"
            echo "  git rebase --continue"
            echo "Or abort:"
            echo "  git rebase --abort"
            exit 1
        fi
        ;;
    M)
        echo "Merging remote changes..."
        git pull origin main

        # Check for merge conflicts
        if git diff --name-only --diff-filter=U | grep -q .; then
            echo "❌ MERGE CONFLICTS"
            echo "Run: /git-merge for guided resolution"
            exit 1
        fi
        ;;
esac
```

### Step 5: Execute Push Operation

Push local commits to remote:

```bash
# Check if anything to push
AHEAD=$(git rev-list --count origin/main..HEAD)

if [ $AHEAD -eq 0 ]; then
    echo "✅ Nothing to push (already up to date)"
    exit 0
fi

# Check for forced push situation
LOCAL_HEAD=$(git rev-parse HEAD)
REMOTE_HEAD=$(git rev-parse origin/main)
MERGE_BASE=$(git merge-base HEAD origin/main)

if [ "$REMOTE_HEAD" != "$MERGE_BASE" ]; then
    echo "⚠️ Would require force push (remote has diverged)"
    echo "This is unusual and may indicate a problem"
    # Handle force push case
else
    # Normal push
    echo "Pushing $AHEAD commit(s) to remote..."
    git push origin main
fi
```

**Push Verification:**

```bash
# Verify push succeeded
if [ $? -eq 0 ]; then
    echo "✅ Push successful"
    git log origin/main..HEAD --oneline | wc -l | xargs -I {} echo "{} commits ahead (should be 0)"
else
    echo "❌ Push failed"
    echo "Check:"
    echo "  1. Network connection"
    echo "  2. Authentication"
    echo "  3. Branch permissions"
    echo "  4. Remote state"
fi
```

### Step 6: Handle Force Push

When force push is necessary (use with extreme caution):

```
⚠️ FORCE PUSH REQUIRED

This will OVERWRITE remote history!

Remote commits that will be lost:
  a3f8d92 - feat: Add feature X
  b7e9c43 - fix: Bug fix Y

Local commits that will replace them:
  c1d2e3f - refactor: Rewritten implementation
  d4e5f6g - test: Updated tests

⚠️ This is DANGEROUS and may affect other team members!

Options:
  [L] Use --force-with-lease (safer)
      → Aborts if remote changed since last fetch

  [F] Use --force (override everything) ⚠️⚠️⚠️
      → Forces push regardless of remote state

  [C] Cancel (recommended)
      → Exit without force pushing

Your choice [L/F/C]:
```

**Force Push Execution:**

```bash
# Safest force push
git push --force-with-lease origin main

# Verify
if [ $? -eq 0 ]; then
    echo "✅ Force push successful"
    echo "⚠️ Notify team members to re-sync!"
else
    echo "❌ Force push failed"
    echo "Remote has new commits since your last fetch"
    echo "Run: git fetch origin"
    echo "Then: git log origin/main to review"
fi
```

### Step 7: Post-Sync Verification

Verify synchronization completed successfully:

```bash
# Fetch to confirm
git fetch origin

# Check sync status
BEHIND=$(git rev-list --count HEAD..origin/main)
AHEAD=$(git rev-list --count origin/main..HEAD)

echo "POST-SYNC STATUS:"
echo "  Commits Behind: $BEHIND"
echo "  Commits Ahead: $AHEAD"

if [ $BEHIND -eq 0 ] && [ $AHEAD -eq 0 ]; then
    echo "  Status: ✅ Fully Synchronized"
elif [ $AHEAD -gt 0 ]; then
    echo "  Status: ⚠️ Local changes not pushed"
elif [ $BEHIND -gt 0 ]; then
    echo "  Status: ⚠️ Remote changes not pulled"
fi
```

### Step 8: Generate Sync Report

Provide comprehensive sync report:

```
═══════════════════════════════════════════════════════
SYNC OPERATION REPORT
═══════════════════════════════════════════════════════

Operation: Full Sync (Pull + Push)
Branch: main ↔ origin/main
Duration: 3.2 seconds

PULL PHASE:
  ✅ Fetched from origin
  ✅ Pulled 2 commits (rebase strategy)
  ✅ No conflicts detected

  Changes pulled:
    c9f7e6d - docs: Update README (2 hours ago)
    a5b8c3f - fix: Resolve timeout issue (5 hours ago)

  Files updated:
    README.md           (+15 -3)
    agent_config.json   (+2 -1)

  Total: 2 files, 17 insertions(+), 4 deletions(-)

PUSH PHASE:
  ✅ Pushed 1 commit to origin

  Commits pushed:
    d1e2f3g - feat: Add workflow engine

  Remote updated successfully

POST-SYNC STATUS:
  Commits Behind: 0 ✅
  Commits Ahead: 0 ✅
  Status: Fully Synchronized

WORKING TREE:
  ✅ Clean (no uncommitted changes)

═══════════════════════════════════════════════════════

💡 RECOMMENDATIONS:
  1. /git-status → Verify repository health
  2. Continue development with confidence
  3. Next sync recommended in 24 hours

═══════════════════════════════════════════════════════
```

## Command Examples

```bash
# Pull latest changes
/git-sync pull

# Push local commits
/git-sync push

# Full sync (pull + push)
/git-sync
/git-sync full

# Dry run (check without executing)
/git-sync --dry-run

# Force push (use with caution)
/git-sync push --force-with-lease

# Sync with specific remote
/git-sync --remote upstream

# Sync specific branch
/git-sync --branch feature-x
```

## Conflict Resolution Workflow

When conflicts are detected during sync:

```
❌ MERGE CONFLICTS DETECTED

The following files have conflicts:
  1. coding_agent_streaming.py
  2. agent_config.json

Current status: MERGING
(Sync operation paused)

Resolution Options:
  [M] Use merge tool
      → /git-merge (guided conflict resolution)

  [V] View conflicts
      → Show conflict markers in each file

  [A] Abort merge
      → git merge --abort (return to pre-sync state)

  [H] Help
      → Show detailed conflict resolution guide

Your choice [M/V/A/H]:
```

**Conflict Resolution Steps:**

1. **View Conflicts:**
```bash
# List conflicted files
git diff --name-only --diff-filter=U

# Show conflict details
git diff <file>

# Show both versions
git show :1:<file>  # common ancestor
git show :2:<file>  # local version
git show :3:<file>  # remote version
```

2. **Resolve Conflicts:**
```
For each file:
  1. Open in editor
  2. Find conflict markers (<<<<<<<, =======, >>>>>>>)
  3. Choose or merge versions
  4. Remove conflict markers
  5. Save file
  6. Stage resolved file: git add <file>
```

3. **Complete Merge:**
```bash
# After resolving all conflicts
git add <resolved-files>

# Continue merge
git merge --continue
# or
git rebase --continue  # if rebasing

# Verify resolution
git log --oneline -1
git diff HEAD^
```

## Edge Cases and Error Handling

| Issue | Detection | Resolution |
|-------|-----------|------------|
| Network failure | `git fetch` fails | Retry with backoff, suggest offline mode |
| Authentication failure | 403/401 errors | Check credentials, suggest re-authentication |
| Detached HEAD | `git symbolic-ref HEAD` fails | Suggest checking out branch first |
| Diverged history | Both ahead and behind | Offer rebase/merge options |
| Uncommitted changes | Working tree dirty | Commit, stash, or cancel |
| Large pull | >100 files changed | Warn user, confirm before pulling |
| Force push to protected branch | Push rejected | Block operation, suggest PR instead |
| Rebase conflicts | Rebase stops | Provide resolution guide or abort option |
| Remote branch deleted | Push to non-existent branch | Suggest creating branch or using different remote |
| No upstream configured | `git push` fails | Configure upstream: `git push -u origin main` |

## Coordination with Other Subagents

### Before Pull: Check with Test Subagent

```
GIT SUBAGENT → TEST SUBAGENT

ABOUT TO:
- Pull 5 commits from remote
- Changes include code modifications

REQUEST:
- Current test status?
- Any uncommitted test results?
- Safe to proceed with pull?

FILES THAT WILL BE UPDATED:
- coding_agent_streaming.py
- workflow_engine.py
- test_phase2.py
```

**Expected Response:**
```
TEST SUBAGENT → GIT SUBAGENT

STATUS:
- All tests passing ✅
- No uncommitted test results
- Safe to pull

RECOMMENDATION:
- Pull remote changes
- Re-run tests after pull
- Notify if test failures occur
```

### After Pull: Notify Test Subagent

```
GIT SUBAGENT → TEST SUBAGENT

COMPLETED:
- Pulled 5 commits from remote
- Code files were modified

ACTION REQUIRED:
- Run test suite to verify compatibility
- Ensure remote changes didn't break tests
- Report any new failures

FILES UPDATED:
- coding_agent_streaming.py (+45 -12)
- workflow_engine.py (+67 -23)
- test_phase2.py (+8 -2)
```

### Before Push: Check with Documentation Subagent

```
GIT SUBAGENT → DOCUMENTATION SUBAGENT

ABOUT TO:
- Push 3 commits to remote
- Includes new feature implementation

REQUEST:
- Is CHANGELOG.md updated?
- Are docs synchronized?
- Ready to push?

COMMITS TO PUSH:
- feat(workflow): Add plan approval system
- test: Add Phase 2 tests
- docs: Update README with workflow examples
```

**Expected Response:**
```
DOCUMENTATION SUBAGENT → GIT SUBAGENT

STATUS:
- CHANGELOG.md updated ✅
- README.md synchronized ✅
- HTML pages generated ✅

RECOMMENDATION:
✅ Ready to push
- All documentation is current
- No sync issues detected
```

### After Push: Notify Documentation

```
GIT SUBAGENT → DOCUMENTATION SUBAGENT

COMPLETED:
- Pushed 3 commits to remote
- Repository now public/available

ACTION REQUIRED:
- Consider deploying documentation
- Update version badges if applicable
- Notify team of new release

PUSHED COMMITS:
- feat(workflow): Add plan approval system
- test: Add Phase 2 tests
- docs: Update README with workflow examples
```

## Sync Strategies Deep Dive

### Fast-Forward Only (Safest)

```bash
git pull --ff-only origin main
```

**Characteristics:**
- ✅ Only succeeds if local is ancestor of remote
- ✅ No merge commits created
- ✅ Linear history preserved
- ❌ Fails if branches diverged

**Use when:**
- No local commits yet
- Starting work session
- Want to ensure simple pull

### Rebase (Recommended)

```bash
git pull --rebase origin main
```

**Characteristics:**
- ✅ Creates linear history
- ✅ Local commits replayed on top of remote
- ✅ Cleaner git log
- ⚠️ Rewrites commit history (changes SHAs)
- ⚠️ More complex conflict resolution

**Use when:**
- Have local commits
- Want clean history
- Working on feature branch
- Conflicts unlikely

**Process:**
```
Before:
  A -- B -- C (main, origin/main)
         \
          D -- E (local commits)

After rebase:
  A -- B -- C (origin/main) -- D' -- E' (main)
```

### Merge (Default)

```bash
git pull origin main
```

**Characteristics:**
- ✅ Preserves all history
- ✅ Shows when branches were merged
- ✅ Simpler conflict resolution
- ❌ Creates merge commits
- ❌ More complex history graph

**Use when:**
- Want complete history
- Multiple people collaborating
- Main branch workflow
- Merge commits acceptable

**Process:**
```
Before:
  A -- B -- C (origin/main)
         \
          D -- E (main)

After merge:
  A -- B -- C ---- F (main, merge commit)
         \        /
          D -- E
```

## Background Sync Mode

Enable automatic background syncing (used by /git-watch):

```bash
# Start background sync monitor
while true; do
    # Check sync status every 5 minutes
    sleep 300

    # Fetch quietly
    git fetch origin 2>&1 | grep -v "From"

    # Check if behind
    BEHIND=$(git rev-list --count HEAD..origin/main)

    if [ $BEHIND -gt 0 ]; then
        echo "[$(date)] ⚠️ Repository behind by $BEHIND commits"
        echo "Run: /git-sync pull"

        # Send notification
        notify "Git Sync" "Remote has $BEHIND new commits"
    fi

    # Check if ahead (reminder to push)
    AHEAD=$(git rev-list --count origin/main..HEAD)

    if [ $AHEAD -gt 5 ]; then
        echo "[$(date)] ⚠️ Local has $AHEAD unpushed commits"
        echo "Run: /git-sync push"
    fi
done
```

## Security Considerations

**Before pulling:**
- Check remote URL is correct
- Verify remote certificate (HTTPS)
- Ensure not pulling from untrusted source

**Before pushing:**
- Scan commits for secrets (run pre-push hook)
- Check branch protection rules
- Verify not pushing sensitive data

**Authentication:**
- Use SSH keys (not passwords)
- Rotate credentials regularly
- Use credential managers

---

**Remember:** Sync early, sync often. A synchronized repository is a happy repository.
