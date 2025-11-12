"""
Phase 2 Test Suite - Workflow Engine Testing

Tests for workflow plans, plan parsing, approval, and execution.
"""

import unittest
import asyncio
import json
import tempfile
from pathlib import Path
import shutil

from plan import Plan, PlanStep, StepStatus
from plan_parser import PlanParser
from workflow_engine import WorkflowEngine, WorkflowStatus
from tool_executor import ToolExecutor


class TestPlanDataStructure(unittest.TestCase):
    """Test Plan and PlanStep classes"""

    def test_plan_step_creation(self):
        """Test creating a plan step"""
        step = PlanStep(
            description="Test step",
            agent_id="main",
            tool="execute_bash",
            arguments={"command": "echo hello"},
            estimated_time=30
        )

        self.assertEqual(step.description, "Test step")
        self.assertEqual(step.agent_id, "main")
        self.assertEqual(step.tool, "execute_bash")
        self.assertEqual(step.status, StepStatus.PENDING)
        self.assertIsNotNone(step.step_id)

    def test_plan_step_serialization(self):
        """Test step to/from dict"""
        step = PlanStep(
            description="Serialize test",
            agent_id="implementer",
            tool="write_file_tool",
            arguments={"path": "./test.txt", "content": "hello"},
            dependencies=["step_1"],
            estimated_time=60
        )

        # Serialize
        data = step.to_dict()
        self.assertEqual(data["description"], "Serialize test")
        self.assertEqual(data["agent_id"], "implementer")

        # Deserialize
        step2 = PlanStep.from_dict(data)
        self.assertEqual(step2.description, step.description)
        self.assertEqual(step2.agent_id, step.agent_id)
        self.assertEqual(step2.tool, step.tool)

    def test_plan_creation(self):
        """Test creating a plan"""
        steps = [
            PlanStep("Step 1", "main", "execute_bash", {"command": "ls"}),
            PlanStep("Step 2", "implementer", "write_file_tool",
                    {"path": "./output.txt", "content": "test"})
        ]

        plan = Plan(
            name="Test Plan",
            description="A test workflow",
            steps=steps
        )

        self.assertEqual(plan.name, "Test Plan")
        self.assertEqual(len(plan.steps), 2)
        self.assertIsNotNone(plan.plan_id)
        self.assertFalse(plan.approved)

    def test_plan_validation_valid(self):
        """Test validation of a valid plan"""
        steps = [
            PlanStep("Step 1", "main", "execute_bash", {"command": "echo 1"}),
            PlanStep("Step 2", "implementer", estimated_time=30)
        ]

        plan = Plan("Valid Plan", "Test", steps)
        is_valid, errors = plan.validate()

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_plan_validation_circular_dependency(self):
        """Test detection of circular dependencies"""
        step1 = PlanStep("Step 1", "main", dependencies=["step_2"])
        step1.step_id = "step_1"

        step2 = PlanStep("Step 2", "main", dependencies=["step_1"])
        step2.step_id = "step_2"

        plan = Plan("Circular Plan", "Test", [step1, step2])
        is_valid, errors = plan.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("circular" in err.lower() for err in errors))

    def test_plan_validation_invalid_agent(self):
        """Test detection of invalid agent ID"""
        steps = [
            PlanStep("Step 1", "invalid_agent", "execute_bash", {"command": "echo 1"})
        ]

        plan = Plan("Invalid Agent Plan", "Test", steps)
        is_valid, errors = plan.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("agent_id" in err.lower() for err in errors))

    def test_plan_validation_invalid_tool(self):
        """Test detection of invalid tool"""
        steps = [
            PlanStep("Step 1", "main", "invalid_tool", {"arg": "value"})
        ]

        plan = Plan("Invalid Tool Plan", "Test", steps)
        is_valid, errors = plan.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("tool" in err.lower() for err in errors))

    def test_plan_execution_order(self):
        """Test dependency resolution and execution order"""
        step1 = PlanStep("Step 1", "main")
        step1.step_id = "step_1"

        step2 = PlanStep("Step 2", "main", dependencies=["step_1"])
        step2.step_id = "step_2"

        step3 = PlanStep("Step 3", "main", dependencies=["step_1", "step_2"])
        step3.step_id = "step_3"

        plan = Plan("Ordered Plan", "Test", [step3, step2, step1])

        execution_order = plan.get_execution_order()

        # step1 should be first, step2 second, step3 last
        self.assertEqual(execution_order[0].step_id, "step_1")
        self.assertEqual(execution_order[1].step_id, "step_2")
        self.assertEqual(execution_order[2].step_id, "step_3")

    def test_plan_progress_tracking(self):
        """Test progress calculation"""
        steps = [
            PlanStep("Step 1", "main"),
            PlanStep("Step 2", "main"),
            PlanStep("Step 3", "main")
        ]

        plan = Plan("Progress Plan", "Test", steps)

        # Initially 0% complete
        completed, total = plan.get_progress()
        self.assertEqual(completed, 0)
        self.assertEqual(total, 3)
        self.assertEqual(plan.get_progress_percentage(), 0.0)

        # Mark one complete
        steps[0].status = StepStatus.COMPLETED
        completed, total = plan.get_progress()
        self.assertEqual(completed, 1)
        self.assertAlmostEqual(plan.get_progress_percentage(), 33.33, places=1)

        # Mark all complete
        steps[1].status = StepStatus.COMPLETED
        steps[2].status = StepStatus.COMPLETED
        self.assertEqual(plan.get_progress_percentage(), 100.0)

    def test_plan_time_estimation(self):
        """Test time estimation"""
        steps = [
            PlanStep("Step 1", "main", estimated_time=30),
            PlanStep("Step 2", "main", estimated_time=60),
            PlanStep("Step 3", "main", estimated_time=45)
        ]

        plan = Plan("Time Plan", "Test", steps)
        total_time = plan.get_total_estimated_time()

        self.assertEqual(total_time, 135)  # 30 + 60 + 45

    def test_plan_cost_estimation(self):
        """Test cost estimation"""
        steps = [
            PlanStep("Step 1", "main"),      # 0.10
            PlanStep("Step 2", "implementer"),  # 0.02
            PlanStep("Step 3", "tester")        # 0.02
        ]

        plan = Plan("Cost Plan", "Test", steps)
        cost = plan.estimate_cost()

        self.assertAlmostEqual(cost, 0.14, places=2)

    def test_plan_json_serialization(self):
        """Test plan to/from JSON"""
        steps = [
            PlanStep("Step 1", "main", "execute_bash", {"command": "ls"}),
            PlanStep("Step 2", "implementer")
        ]

        plan = Plan("JSON Plan", "Serialization test", steps)
        plan.approved = True

        # Serialize to JSON
        json_str = plan.to_json()
        self.assertIsInstance(json_str, str)

        # Deserialize
        plan2 = Plan.from_json(json_str)
        self.assertEqual(plan2.name, plan.name)
        self.assertEqual(plan2.description, plan.description)
        self.assertEqual(len(plan2.steps), len(plan.steps))
        self.assertEqual(plan2.approved, plan.approved)


class TestPlanParser(unittest.TestCase):
    """Test PlanParser class"""

    def setUp(self):
        self.parser = PlanParser()

    def test_has_plan_detection(self):
        """Test detecting [PLAN] tags"""
        text_with_plan = "Some text\n[PLAN]\nWorkflow here\n[/PLAN]\nMore text"
        text_without_plan = "Just regular text without plan tags"

        self.assertTrue(self.parser.has_plan(text_with_plan))
        self.assertFalse(self.parser.has_plan(text_without_plan))

    def test_extract_plan_text(self):
        """Test extracting plan content"""
        text = "Intro\n[PLAN]\nPlan content here\n[/PLAN]\nOutro"

        content = self.parser.extract_plan_text(text)

        self.assertIsNotNone(content)
        self.assertEqual(content, "Plan content here")

    def test_parse_workflow_plan(self):
        """Test parsing a complete workflow plan"""
        plan_text = """
[PLAN]
## Workflow: Test Workflow

This is a test workflow with multiple steps.

### Step 1: Create test file
- Agent: implementer
- Tool: write_file_tool
- Arguments: {"path": "./test.txt", "content": "hello"}
- Dependencies: none
- Estimated Time: 30s

### Step 2: Read test file
- Agent: reviewer
- Tool: read_file_tool
- Arguments: {"path": "./test.txt"}
- Dependencies: Step 1
- Estimated Time: 10s

## Total Estimated Time: 40s
## Cost Estimate: $0.04
[/PLAN]
"""

        plan = self.parser.parse_plan(plan_text)

        self.assertIsNotNone(plan)
        self.assertEqual(plan.name, "Test Workflow")
        self.assertEqual(len(plan.steps), 2)

        # Check first step
        step1 = plan.steps[0]
        self.assertIn("Create test file", step1.description)
        self.assertEqual(step1.agent_id, "implementer")
        self.assertEqual(step1.tool, "write_file_tool")
        self.assertEqual(step1.estimated_time, 30)

        # Check second step
        step2 = plan.steps[1]
        self.assertEqual(step2.agent_id, "reviewer")
        self.assertEqual(step2.tool, "read_file_tool")

    def test_parse_time_units(self):
        """Test parsing different time units"""
        # Seconds
        self.assertEqual(self.parser._parse_time("30s"), 30)
        self.assertEqual(self.parser._parse_time("45 seconds"), 45)

        # Minutes
        self.assertEqual(self.parser._parse_time("2m"), 120)
        self.assertEqual(self.parser._parse_time("5 minutes"), 300)

        # Hours
        self.assertEqual(self.parser._parse_time("1h"), 3600)
        self.assertEqual(self.parser._parse_time("2 hours"), 7200)


class TestWorkflowEngine(unittest.IsolatedAsyncioTestCase):
    """Test WorkflowEngine class"""

    def setUp(self):
        """Set up test environment"""
        # Create temp directory
        self.test_dir = Path(tempfile.mkdtemp())

        # Create test config
        self.config = {
            "agent_settings": {
                "safe_mode": True,
                "timeout_seconds": 60
            },
            "file_operations": {
                "allow_file_write": True,
                "allow_file_read": True,
                "allowed_directories": [str(self.test_dir)],
                "max_file_size_kb": 500
            }
        }

        self.tool_executor = ToolExecutor(self.config)
        self.engine = WorkflowEngine(
            tool_executor=self.tool_executor,
            checkpoint_dir=self.test_dir / "checkpoints"
        )

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    async def test_execute_simple_plan(self):
        """Test executing a simple 1-step plan"""
        test_file = self.test_dir / "simple_test.txt"

        step = PlanStep(
            "Write test file",
            "main",
            "write_file_tool",
            {"path": str(test_file), "content": "Hello World"}
        )

        plan = Plan("Simple Plan", "Write a file", [step])
        plan.approved = True

        success, message = await self.engine.execute_plan(plan)

        self.assertTrue(success)
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "Hello World")

    async def test_execute_multi_step_plan(self):
        """Test executing a multi-step plan"""
        test_file = self.test_dir / "multi_test.txt"

        step1 = PlanStep(
            "Write file",
            "main",
            "write_file_tool",
            {"path": str(test_file), "content": "Step 1"}
        )
        step1.step_id = "step_1"

        step2 = PlanStep(
            "List files",
            "main",
            "list_files_tool",
            {"path": str(self.test_dir), "pattern": "*.txt"},
            dependencies=["step_1"]
        )
        step2.step_id = "step_2"

        plan = Plan("Multi-Step Plan", "Write and list", [step1, step2])
        plan.approved = True

        success, message = await self.engine.execute_plan(plan)

        self.assertTrue(success)
        self.assertEqual(step1.status, StepStatus.COMPLETED)
        self.assertEqual(step2.status, StepStatus.COMPLETED)

    async def test_checkpoint_creation(self):
        """Test that checkpoints are created"""
        test_file = self.test_dir / "checkpoint_test.txt"
        test_file.write_text("Original content")

        step = PlanStep(
            "Overwrite file",
            "main",
            "write_file_tool",
            {"path": str(test_file), "content": "New content"}
        )

        plan = Plan("Checkpoint Plan", "Test checkpoints", [step])
        plan.approved = True

        await self.engine.execute_plan(plan)

        # Check that checkpoint was created
        self.assertGreater(len(self.engine.checkpoints), 0)

    async def test_unapproved_plan_rejection(self):
        """Test that unapproved plans are rejected"""
        step = PlanStep("Test", "main")
        plan = Plan("Unapproved", "Not approved", [step])
        plan.approved = False

        success, message = await self.engine.execute_plan(plan)

        self.assertFalse(success)
        self.assertIn("not approved", message.lower())

    async def test_invalid_plan_rejection(self):
        """Test that invalid plans are rejected"""
        step = PlanStep("Invalid", "invalid_agent")
        plan = Plan("Invalid", "Bad plan", [step])
        plan.approved = True

        success, message = await self.engine.execute_plan(plan)

        self.assertFalse(success)
        self.assertIn("validation failed", message.lower())

    async def test_execution_summary(self):
        """Test getting execution summary"""
        step = PlanStep("Test step", "main")
        plan = Plan("Summary Test", "Test", [step])
        plan.approved = True

        await self.engine.execute_plan(plan)

        summary = self.engine.get_execution_summary()

        self.assertEqual(summary["plan_name"], "Summary Test")
        self.assertIn("status", summary)
        self.assertIn("steps_completed", summary)
        self.assertIn("total_execution_time", summary)


class TestIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests"""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = {
            "agent_settings": {"safe_mode": True, "timeout_seconds": 60},
            "file_operations": {
                "allow_file_write": True,
                "allow_file_read": True,
                "allowed_directories": [str(self.test_dir)],
                "max_file_size_kb": 500
            }
        }
        self.tool_executor = ToolExecutor(self.config)
        self.parser = PlanParser()
        self.engine = WorkflowEngine(self.tool_executor, checkpoint_dir=self.test_dir / "checkpoints")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    async def test_end_to_end_workflow(self):
        """Test complete workflow: parse → execute"""
        plan_text = f"""
[PLAN]
## Workflow: End-to-End Test

### Step 1: Create file
- Agent: implementer
- Tool: write_file_tool
- Arguments: {{"path": "{self.test_dir}/e2e.txt", "content": "E2E Test"}}
- Dependencies: none
- Estimated Time: 30s

### Step 2: Verify file
- Agent: tester
- Tool: read_file_tool
- Arguments: {{"path": "{self.test_dir}/e2e.txt"}}
- Dependencies: Step 1
- Estimated Time: 10s
[/PLAN]
"""

        # Parse
        plan = self.parser.parse_plan(plan_text)
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan.steps), 2)

        # Execute
        plan.approved = True
        success, message = await self.engine.execute_plan(plan)

        self.assertTrue(success)
        self.assertTrue((self.test_dir / "e2e.txt").exists())


def run_tests():
    """Run all Phase 2 tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPlanDataStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestPlanParser))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate summary
    print("\n" + "=" * 70)
    print("PHASE 2 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Pass Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)

    # Save results to JSON
    results_data = {
        "timestamp": "2025-11-11",
        "tests_run": result.testsRun,
        "successes": result.testsRun - len(result.failures) - len(result.errors),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "pass_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    }

    with open("phase2_test_results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    print("\n✅ Results saved to phase2_test_results.json\n")

    return result


if __name__ == "__main__":
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
