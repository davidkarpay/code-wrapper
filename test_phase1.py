#!/usr/bin/env python3
"""
Phase 1 Testing Suite
Tests automatic spawning, tool execution, and file operations
"""

import sys
import json
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tool_executor import ToolExecutor, ExecutionResult
from agent_manager import AgentManager
from multi_agent_orchestrator import MultiAgentOrchestrator


class Phase1TestSuite:
    """Test suite for Phase 1 functionality"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")

        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    async def test_tool_executor_initialization(self):
        """Test 1: ToolExecutor can be initialized"""
        test_name = "ToolExecutor Initialization"
        try:
            config = {
                "agent_settings": {
                    "safe_mode": True,
                    "timeout_seconds": 60,
                    "timeout_overrides": {"code_execution": 180}
                },
                "file_operations": {
                    "allow_file_write": True,
                    "allow_file_read": True,
                    "allowed_directories": ["./test_workspace", "./agent_workspace"],
                    "max_file_size_kb": 500
                }
            }
            executor = ToolExecutor(config)
            self.log_test(test_name, True, "ToolExecutor created successfully")
            return executor
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")
            return None

    async def test_safe_bash_commands(self, executor: ToolExecutor):
        """Test 2: Safe bash commands execute successfully"""
        test_name = "Safe Bash Command Execution"
        try:
            # Test safe commands
            result = await executor.execute_bash("echo 'Hello World'")

            if result.success and "Hello World" in result.stdout:
                self.log_test(test_name, True, f"Echo command worked: {result.stdout.strip()}")
            else:
                self.log_test(test_name, False, f"Echo failed: {result.error_message}")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_dangerous_commands_blocked(self, executor: ToolExecutor):
        """Test 3: Dangerous commands are blocked"""
        test_name = "Dangerous Command Blocking"
        try:
            # Test dangerous command
            result = await executor.execute_bash("rm -rf /")

            if not result.success and "blocked" in result.error_message.lower():
                self.log_test(test_name, True, "Dangerous 'rm' command blocked as expected")
            else:
                self.log_test(test_name, False, "Dangerous command was NOT blocked!")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_file_write_operations(self, executor: ToolExecutor):
        """Test 4: File write operations work in allowed directories"""
        test_name = "File Write Operations"
        try:
            # Create test directory
            test_dir = Path("./test_workspace")
            test_dir.mkdir(exist_ok=True)

            test_file = test_dir / "phase1_test.txt"
            test_content = "Phase 1 test content\nLine 2\nLine 3"

            result = await executor.write_file(test_file, test_content, overwrite=True)

            if result.success:
                # Verify file was written
                if test_file.exists():
                    actual_content = test_file.read_text()
                    if actual_content == test_content:
                        self.log_test(test_name, True, f"File written successfully: {test_file}")
                    else:
                        self.log_test(test_name, False, "File content mismatch")
                else:
                    self.log_test(test_name, False, "File not created")
            else:
                self.log_test(test_name, False, f"Write failed: {result.error_message}")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_file_read_operations(self, executor: ToolExecutor):
        """Test 5: File read operations work"""
        test_name = "File Read Operations"
        try:
            test_file = Path("./test_workspace/phase1_test.txt")

            if not test_file.exists():
                self.log_test(test_name, False, "Test file doesn't exist (write test may have failed)")
                return

            result = await executor.read_file(test_file)

            if result.success and "Phase 1 test content" in result.stdout:
                self.log_test(test_name, True, f"File read successfully ({len(result.stdout)} bytes)")
            else:
                self.log_test(test_name, False, f"Read failed: {result.error_message}")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_directory_restrictions(self, executor: ToolExecutor):
        """Test 6: Files outside allowed directories are blocked"""
        test_name = "Directory Restriction Enforcement"
        try:
            # Try to write to a disallowed directory
            forbidden_file = Path("/tmp/forbidden_test.txt")
            result = await executor.write_file(forbidden_file, "Should fail", overwrite=True)

            if not result.success and "not in allowed directories" in result.error_message:
                self.log_test(test_name, True, "Correctly blocked access to disallowed directory")
            else:
                self.log_test(test_name, False, "Failed to block disallowed directory access!")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_python_script_execution(self, executor: ToolExecutor):
        """Test 7: Python script execution works"""
        test_name = "Python Script Execution"
        try:
            # Create a test script
            test_dir = Path("./test_workspace")
            test_dir.mkdir(exist_ok=True)

            script_path = test_dir / "test_script.py"
            script_content = """#!/usr/bin/env python3
print("Script started")
print("Test calculation:", 2 + 2)
print("Script completed")
"""
            script_path.write_text(script_content)

            result = await executor.execute_python_script(script_path)

            if result.success and "Test calculation: 4" in result.stdout:
                self.log_test(test_name, True, "Python script executed successfully")
            else:
                self.log_test(test_name, False, f"Script execution failed: {result.error_message or result.stderr}")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_list_files_operation(self, executor: ToolExecutor):
        """Test 8: List files operation works"""
        test_name = "List Files Operation"
        try:
            test_dir = Path("./test_workspace")
            result = await executor.list_files(test_dir, "*.txt")

            if result.success:
                files = json.loads(result.stdout)
                txt_files = [f for f in files if f["name"].endswith(".txt")]

                if len(txt_files) > 0:
                    self.log_test(test_name, True, f"Found {len(txt_files)} .txt files")
                else:
                    self.log_test(test_name, False, "No .txt files found (write test may have failed)")
            else:
                self.log_test(test_name, False, f"List failed: {result.error_message}")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_config_loading(self):
        """Test 9: Multi-agent config loads correctly"""
        test_name = "Multi-Agent Config Loading"
        try:
            from async_streaming_agent import load_multi_agent_config

            config = load_multi_agent_config("agent_config_multi_agent.json")

            # Check critical settings
            checks = [
                ("spawning_rules" in config, "spawning_rules present"),
                ("agent_profiles" in config, "agent_profiles present"),
                ("file_operations" in config, "file_operations present"),
                (config.get("spawning_rules", {}).get("auto_spawn_on_keywords") is not None, "auto_spawn_on_keywords defined")
            ]

            all_passed = all(check[0] for check in checks)

            if all_passed:
                self.log_test(test_name, True, "Config loaded with all required sections")
            else:
                failed_checks = [check[1] for check in checks if not check[0]]
                self.log_test(test_name, False, f"Missing: {', '.join(failed_checks)}")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_keyword_mapping(self):
        """Test 10: Keyword mappings are configured correctly"""
        test_name = "Keyword Mapping Configuration"
        try:
            from async_streaming_agent import load_multi_agent_config

            config = load_multi_agent_config("agent_config_multi_agent.json")
            keywords = config.get("spawning_rules", {}).get("keywords", {})

            required_keywords = ["review", "test", "research", "implement", "optimize"]
            missing = [kw for kw in required_keywords if kw not in keywords]

            if not missing:
                self.log_test(test_name, True, f"All {len(required_keywords)} required keywords configured")
            else:
                self.log_test(test_name, False, f"Missing keywords: {', '.join(missing)}")
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def run_all_tests(self):
        """Run all Phase 1 tests"""
        print("=" * 70)
        print("PHASE 1 TEST SUITE")
        print("=" * 70)
        print()

        # Initialize ToolExecutor
        executor = await self.test_tool_executor_initialization()

        if executor:
            # Run tool execution tests
            await self.test_safe_bash_commands(executor)
            await self.test_dangerous_commands_blocked(executor)
            await self.test_file_write_operations(executor)
            await self.test_file_read_operations(executor)
            await self.test_directory_restrictions(executor)
            await self.test_python_script_execution(executor)
            await self.test_list_files_operation(executor)

        # Run config tests
        await self.test_config_loading()
        await self.test_keyword_mapping()

        # Print summary
        print()
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_passed + self.tests_failed}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")

        pass_rate = (self.tests_passed / (self.tests_passed + self.tests_failed) * 100) if (self.tests_passed + self.tests_failed) > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%")
        print("=" * 70)

        # Save results to JSON
        results = {
            "phase": "Phase 1",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "pass_rate": pass_rate,
            "test_results": self.test_results
        }

        results_file = Path("phase1_test_results.json")
        results_file.write_text(json.dumps(results, indent=2))
        print(f"\n📄 Results saved to: {results_file}")

        return self.tests_failed == 0


async def main():
    """Main test runner"""
    suite = Phase1TestSuite()
    success = await suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
