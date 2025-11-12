#!/usr/bin/env python3
"""
Automated Test Suite for coding_agent_streaming.py File Operations
Tests file read/write/edit operations and security controls programmatically
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add current directory to path to import the agent
sys.path.insert(0, str(Path(__file__).parent))

try:
    from coding_agent_streaming import StreamingAgent, AgentConfig
except ImportError as e:
    print(f"Error importing agent: {e}")
    sys.exit(1)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []

    def add_result(self, test_name, status, expected, actual, notes=""):
        self.results.append({
            "test": test_name,
            "status": status,
            "expected": expected,
            "actual": actual,
            "notes": notes
        })
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "SKIP":
            self.skipped += 1

    def print_summary(self):
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {self.passed} ✓")
        print(f"Failed: {self.failed} ✗")
        print(f"Skipped: {self.skipped} ○")
        print(f"Pass Rate: {(self.passed / len(self.results) * 100) if self.results else 0:.1f}%")
        print("=" * 70)


def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'─' * 70}")
    print(f"TEST: {test_name}")
    print(f"{'─' * 70}")


def test_file_read_operations(agent, results):
    """Test FILE_READ operations"""
    print("\n" + "=" * 70)
    print("PHASE 2: FILE_READ OPERATIONS")
    print("=" * 70)

    # Test 2.1: Read existing small file
    print_test_header("2.1: Read Existing Small File")
    success, content = agent.read_file("test_workspace/test_read.txt")
    expected = "Should succeed and return file content"
    actual = f"Success: {success}, Content length: {len(content) if success else 'N/A'}"
    if success and len(content) > 0:
        results.add_result("2.1 Read Small File", "PASS", expected, actual)
        print(f"✓ PASS - File read successfully ({len(content)} chars)")
    else:
        results.add_result("2.1 Read Small File", "FAIL", expected, actual, content)
        print(f"✗ FAIL - {content}")

    # Test 2.2: Read non-existent file
    print_test_header("2.2: Read Non-Existent File")
    success, content = agent.read_file("test_workspace/does_not_exist.txt")
    expected = "Should fail with 'File does not exist'"
    actual = f"Success: {success}, Error: {content if not success else 'N/A'}"
    if not success and "does not exist" in content.lower():
        results.add_result("2.2 Read Non-Existent", "PASS", expected, actual)
        print(f"✓ PASS - Correctly rejected non-existent file")
    else:
        results.add_result("2.2 Read Non-Existent", "FAIL", expected, actual)
        print(f"✗ FAIL - Should have failed")

    # Test 2.3: Read large file (size limit)
    print_test_header("2.3: Read Large File (Size Limit)")
    success, content = agent.read_file("test_workspace/test_read_large.txt")
    expected = "Should fail with 'File too large'"
    actual = f"Success: {success}, Error: {content if not success else 'N/A'}"
    if not success and "too large" in content.lower():
        results.add_result("2.3 Read Large File", "PASS", expected, actual)
        print(f"✓ PASS - Size limit enforced")
    else:
        results.add_result("2.3 Read Large File", "FAIL", expected, actual)
        print(f"✗ FAIL - Size limit not enforced correctly")

    # Test 2.4: Read file outside allowed directories
    print_test_header("2.4: Read Outside Allowed Directories")
    success, content = agent.read_file("/etc/passwd")
    expected = "Should fail with 'not in allowed directories'"
    actual = f"Success: {success}, Error: {content if not success else 'N/A'}"
    if not success and "allowed directories" in content.lower():
        results.add_result("2.4 Directory Restriction", "PASS", expected, actual)
        print(f"✓ PASS - Directory restriction enforced")
    else:
        results.add_result("2.4 Directory Restriction", "FAIL", expected, actual)
        print(f"✗ FAIL - Directory restriction not working")


def test_file_write_operations(agent, results):
    """Test FILE_WRITE operations"""
    print("\n" + "=" * 70)
    print("PHASE 3: FILE_WRITE OPERATIONS")
    print("=" * 70)

    # Test 3.1: Create new file
    print_test_header("3.1: Create New File")
    test_content = "This is a test file created by automated tests."
    success, message = agent.write_file("test_workspace/test_write_auto.txt", test_content)
    expected = "Should create file successfully"
    actual = f"Success: {success}, Message: {message}"
    if success:
        # Verify file was created
        if Path("test_workspace/test_write_auto.txt").exists():
            results.add_result("3.1 Create New File", "PASS", expected, actual)
            print(f"✓ PASS - File created successfully")
        else:
            results.add_result("3.1 Create New File", "FAIL", expected, "File not found after write")
            print(f"✗ FAIL - File not found after write")
    else:
        results.add_result("3.1 Create New File", "FAIL", expected, actual)
        print(f"✗ FAIL - {message}")

    # Test 3.2: Write file with large content (>500KB) - should fail
    print_test_header("3.2: Write Large Content (Size Limit)")
    large_content = "X" * (600 * 1024)  # 600KB
    success, message = agent.write_file("test_workspace/test_write_large.txt", large_content)
    expected = "Should fail with 'Content too large'"
    actual = f"Success: {success}, Message: {message}"
    if not success and "too large" in message.lower():
        results.add_result("3.2 Write Size Limit", "PASS", expected, actual)
        print(f"✓ PASS - Size limit enforced on write")
    else:
        results.add_result("3.2 Write Size Limit", "FAIL", expected, actual)
        print(f"✗ FAIL - Size limit not enforced")

    # Test 3.3: Write outside allowed directories
    print_test_header("3.3: Write Outside Allowed Directories")
    success, message = agent.write_file("/tmp/test_unauthorized.txt", "content")
    expected = "Should fail with 'not in allowed directories'"
    actual = f"Success: {success}, Message: {message}"
    if not success and "allowed directories" in message.lower():
        results.add_result("3.3 Write Directory Restriction", "PASS", expected, actual)
        print(f"✓ PASS - Directory restriction enforced")
    else:
        results.add_result("3.3 Write Directory Restriction", "FAIL", expected, actual)
        print(f"✗ FAIL - Directory restriction not working")

    # Test 3.4: Toggle write permission off
    print_test_header("3.4: Write Permission Toggle")
    original_permission = agent.config.allow_file_write
    agent.config.allow_file_write = False
    success, message = agent.write_file("test_workspace/test_no_perm.txt", "content")
    expected = "Should fail with 'writing is disabled'"
    actual = f"Success: {success}, Message: {message}"
    agent.config.allow_file_write = original_permission  # Restore

    if not success and "disabled" in message.lower():
        results.add_result("3.4 Write Permission", "PASS", expected, actual)
        print(f"✓ PASS - Permission flag enforced")
    else:
        results.add_result("3.4 Write Permission", "FAIL", expected, actual)
        print(f"✗ FAIL - Permission flag not enforced")


def test_file_edit_operations(agent, results):
    """Test FILE_EDIT operations"""
    print("\n" + "=" * 70)
    print("PHASE 4: FILE_EDIT OPERATIONS")
    print("=" * 70)

    # Test 4.1: Edit file with find/replace
    print_test_header("4.1: Edit File (Find/Replace)")
    success, message = agent.edit_file(
        "test_workspace/test_edit.txt",
        "OLD_VALUE",
        "UPDATED_VALUE"
    )
    expected = "Should replace text and create backup"
    actual = f"Success: {success}, Message: {message}"

    if success:
        # Check if backup was created
        backup_exists = Path("test_workspace/test_edit.txt.backup").exists()
        # Check if replacement occurred
        with open("test_workspace/test_edit.txt", 'r') as f:
            content = f.read()
        replaced = "UPDATED_VALUE" in content and "OLD_VALUE" not in content

        if backup_exists and replaced:
            results.add_result("4.1 Edit Find/Replace", "PASS", expected, actual + " (backup created, text replaced)")
            print(f"✓ PASS - Edit successful, backup created")
        else:
            results.add_result("4.1 Edit Find/Replace", "FAIL", expected,
                             f"Backup exists: {backup_exists}, Text replaced: {replaced}")
            print(f"✗ FAIL - Backup: {backup_exists}, Replaced: {replaced}")
    else:
        results.add_result("4.1 Edit Find/Replace", "FAIL", expected, actual)
        print(f"✗ FAIL - {message}")

    # Test 4.2: Edit with non-existent find text
    print_test_header("4.2: Edit Non-Existent Text")
    success, message = agent.edit_file(
        "test_workspace/test_edit.txt",
        "NONEXISTENT_TEXT_12345",
        "REPLACEMENT"
    )
    expected = "Should fail with 'not found'"
    actual = f"Success: {success}, Message: {message}"

    if not success and "not found" in message.lower():
        results.add_result("4.2 Edit Not Found", "PASS", expected, actual)
        print(f"✓ PASS - Correctly rejected non-existent text")
    else:
        results.add_result("4.2 Edit Not Found", "FAIL", expected, actual)
        print(f"✗ FAIL - Should have failed")

    # Test 4.3: Edit file outside allowed directories
    print_test_header("4.3: Edit Outside Allowed Directories")
    success, message = agent.edit_file("/etc/passwd", "root", "test")
    expected = "Should fail with 'not in allowed directories'"
    actual = f"Success: {success}, Message: {message}"

    if not success and "allowed directories" in message.lower():
        results.add_result("4.3 Edit Directory Restriction", "PASS", expected, actual)
        print(f"✓ PASS - Directory restriction enforced")
    else:
        results.add_result("4.3 Edit Directory Restriction", "FAIL", expected, actual)
        print(f"✗ FAIL - Directory restriction not working")

    # Test 4.4: Edit permission toggle
    print_test_header("4.4: Edit Permission Toggle")
    original_permission = agent.config.allow_file_edit
    agent.config.allow_file_edit = False
    success, message = agent.edit_file("test_workspace/test_edit.txt", "test", "test2")
    expected = "Should fail with 'editing is disabled'"
    actual = f"Success: {success}, Message: {message}"
    agent.config.allow_file_edit = original_permission  # Restore

    if not success and "disabled" in message.lower():
        results.add_result("4.4 Edit Permission", "PASS", expected, actual)
        print(f"✓ PASS - Permission flag enforced")
    else:
        results.add_result("4.4 Edit Permission", "FAIL", expected, actual)
        print(f"✗ FAIL - Permission flag not enforced")


def test_security_controls(agent, results):
    """Test security controls"""
    print("\n" + "=" * 70)
    print("PHASE 6: SECURITY CONTROLS")
    print("=" * 70)

    # Test 6.1: Path traversal attack
    print_test_header("6.1: Path Traversal Attack")
    success, content = agent.read_file("../../../etc/passwd")
    expected = "Should block path traversal"
    actual = f"Success: {success}, Message: {content if not success else 'SECURITY BREACH!'}"

    if not success:
        results.add_result("6.1 Path Traversal", "PASS", expected, actual)
        print(f"✓ PASS - Path traversal blocked")
    else:
        results.add_result("6.1 Path Traversal", "FAIL", expected, "SECURITY VULNERABILITY: Path traversal allowed!")
        print(f"✗ FAIL - SECURITY ISSUE: Path traversal not blocked!")

    # Test 6.2: Absolute path outside allowed dirs
    print_test_header("6.2: Absolute Path Outside Allowed")
    success, content = agent.read_file("/tmp/test.txt")
    expected = "Should reject absolute path outside allowed"
    actual = f"Success: {success}"

    if not success:
        results.add_result("6.2 Absolute Path", "PASS", expected, actual)
        print(f"✓ PASS - Absolute path restricted")
    else:
        results.add_result("6.2 Absolute Path", "FAIL", expected, actual)
        print(f"✗ FAIL - Absolute path not restricted")

    # Test 6.3: Create file at 500KB boundary
    print_test_header("6.3: Size Limit Boundary (500KB)")
    boundary_content = "X" * (500 * 1024)  # Exactly 500KB
    success, message = agent.write_file("test_workspace/test_500kb.txt", boundary_content)
    expected = "At boundary: should succeed or fail consistently"
    actual = f"Success: {success}, Message: {message}"

    # This is a boundary test - document the behavior
    results.add_result("6.3 Size Boundary", "PASS" if success else "FAIL", expected,
                      actual + " (Boundary behavior documented)")
    if success:
        print(f"✓ Note: 500KB exactly is ALLOWED")
    else:
        print(f"✓ Note: 500KB exactly is REJECTED")


def test_path_validation(agent, results):
    """Test path validation logic"""
    print("\n" + "=" * 70)
    print("ADDITIONAL: PATH VALIDATION TESTS")
    print("=" * 70)

    # Test relative path
    print_test_header("Path: Relative Path")
    success, content = agent.read_file("./test_workspace/test_read.txt")
    expected = "Should resolve relative path correctly"
    if success:
        results.add_result("Path Relative", "PASS", expected, "Relative path accepted")
        print(f"✓ PASS - Relative path works")
    else:
        results.add_result("Path Relative", "FAIL", expected, content)
        print(f"✗ FAIL - {content}")

    # Test path with spaces (if exists)
    print_test_header("Path: Path Normalization")
    success, content = agent.read_file("test_workspace/../test_workspace/test_read.txt")
    expected = "Should normalize path correctly"
    if success:
        results.add_result("Path Normalization", "PASS", expected, "Path normalized")
        print(f"✓ PASS - Path normalization works")
    else:
        results.add_result("Path Normalization", "FAIL", expected, content)
        print(f"✗ FAIL - {content}")


def check_filesystem_state(results):
    """Check filesystem state after tests"""
    print("\n" + "=" * 70)
    print("PHASE 8: FILESYSTEM VERIFICATION")
    print("=" * 70)

    test_dir = Path("test_workspace")

    # Check test files exist
    print_test_header("8.1: Verify Test Files")
    expected_files = ["test_read.txt", "test_edit.txt", "test_read_large.txt"]
    all_exist = all((test_dir / f).exists() for f in expected_files)

    if all_exist:
        results.add_result("8.1 Test Files Exist", "PASS", "All test files should exist", "All found")
        print(f"✓ PASS - All original test files exist")
    else:
        missing = [f for f in expected_files if not (test_dir / f).exists()]
        results.add_result("8.1 Test Files Exist", "FAIL", "All test files should exist",
                          f"Missing: {missing}")
        print(f"✗ FAIL - Missing files: {missing}")

    # Check backup file
    print_test_header("8.2: Verify Backup File")
    backup_file = test_dir / "test_edit.txt.backup"
    if backup_file.exists():
        results.add_result("8.2 Backup Created", "PASS", "Backup file should exist", "Backup found")
        print(f"✓ PASS - Backup file created")
    else:
        results.add_result("8.2 Backup Created", "FAIL", "Backup file should exist", "Backup not found")
        print(f"✗ FAIL - Backup file not created")

    # List all files
    print_test_header("8.3: List All Files")
    files = sorted(test_dir.iterdir())
    print(f"Files in test_workspace:")
    for f in files:
        size = f.stat().st_size if f.is_file() else 0
        print(f"  - {f.name} ({size / 1024:.1f} KB)")

    results.add_result("8.3 List Files", "PASS", "Should list files", f"Found {len(files)} files")


def main():
    """Run all automated tests"""
    print("=" * 70)
    print("AUTOMATED FILE OPERATIONS TEST SUITE")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {Path.cwd()}")
    print("=" * 70)

    results = TestResults()

    try:
        # Initialize agent
        print("\nInitializing StreamingAgent...")
        agent = StreamingAgent()
        print(f"✓ Agent initialized")
        print(f"  Provider: {agent.config.provider}")
        print(f"  Model: {agent.config.model_name}")
        print(f"  Max file size: {agent.config.max_file_size_kb} KB")
        print(f"  Allowed directories: {agent.config.allowed_directories}")

        # Run test phases
        test_file_read_operations(agent, results)
        test_file_write_operations(agent, results)
        test_file_edit_operations(agent, results)
        test_security_controls(agent, results)
        test_path_validation(agent, results)
        check_filesystem_state(results)

        # Print summary
        results.print_summary()

        # Save results to JSON
        output_file = "automated_test_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": len(results.results),
                    "passed": results.passed,
                    "failed": results.failed,
                    "skipped": results.skipped
                },
                "tests": results.results
            }, f, indent=2)
        print(f"\n✓ Results saved to: {output_file}")

        # Return exit code based on failures
        return 0 if results.failed == 0 else 1

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
