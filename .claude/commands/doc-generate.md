---
description: Regenerate all HTML documentation pages from markdown sources
allowed-tools: Bash(python:*), Read
---

Regenerate all HTML documentation pages from markdown sources.

You are the **Documentation Subagent** for the code_wrapper project.

## Your Role

You specialize in converting markdown documentation to HTML pages using the automated generation script.

## Task

Regenerate HTML documentation pages from their markdown source files.

## Steps to Follow

1. **Execute** the generation script:
   ```bash
   python generate_test_docs.py
   ```

2. **Monitor** the output for:
   - Success messages (✅ Generated: ...)
   - Error messages
   - Warnings or issues

3. **Verify** all HTML pages were created:
   - `test-documentation/test-results.html`
   - `test-documentation/recommendations.html`
   - `test-documentation/test-plan.html`
   - `test-documentation/summary.html`

4. **Check** file sizes and timestamps:
   ```bash
   ls -lh test-documentation/*.html
   ```

5. **Report** results:
   - Number of pages regenerated
   - Any errors encountered
   - File sizes (should be reasonable, not 0 bytes)
   - Success confirmation

## What This Script Does

The `generate_test_docs.py` script:
- Reads markdown source files
- Converts markdown to HTML with proper formatting
- Applies consistent styling and navigation
- Generates table of contents
- Creates collapsible sections
- Adds badges and status indicators
- Preserves code blocks and tables

## Markdown → HTML Mappings

| Source File | Output HTML |
|------------|-------------|
| `test_results.md` | `test-documentation/test-results.html` |
| `test_recommendations.md` | `test-documentation/recommendations.html` |
| `test_plan.md` | `test-documentation/test-plan.html` |
| `TESTING_SUMMARY.md` | `test-documentation/summary.html` |

## Advanced Usage

### Generate Single Page
```bash
python generate_test_docs.py --page test-results
python generate_test_docs.py --page recommendations
python generate_test_docs.py --page test-plan
python generate_test_docs.py --page summary
```

### List Available Pages
```bash
python generate_test_docs.py --list
```

### Get Help
```bash
python generate_test_docs.py --help
```

## When to Use This Command

**Use `/doc-generate` when:**
- Multiple markdown files have been updated
- You want to regenerate everything from scratch
- Troubleshooting HTML generation issues
- After major documentation updates
- Before deploying documentation

**Use `/doc-update` instead when:**
- Only one specific file needs updating
- You want more control over the process
- You need to review changes before regenerating

## Error Handling

**If generation fails:**
1. Check that source markdown files exist
2. Verify Python is available: `python --version`
3. Check for syntax errors in markdown
4. Ensure `test-documentation/` directory exists
5. Verify script permissions: `ls -l generate_test_docs.py`
6. Try generating single pages to isolate the issue

**Common Errors:**
- **FileNotFoundError**: Source markdown file missing
- **PermissionError**: Can't write to test-documentation/
- **SyntaxError**: Malformed markdown or script issue
- **ImportError**: Missing Python dependencies

## Quality Checks

After regeneration, verify:
- ✅ All 4 HTML files exist
- ✅ File sizes are reasonable (>10KB each)
- ✅ Timestamps are current
- ✅ No Python errors in output
- ✅ Navigation links work (spot check)

## Coordination

**Trigger this command after:**
- Test subagent updates test results
- Multiple documentation files are modified
- Major project milestones
- Before sharing documentation externally

---

**Remember:** This is a batch operation. Use `/doc-update` for targeted updates, or this command for comprehensive regeneration.
