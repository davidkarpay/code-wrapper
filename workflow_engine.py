"""
Workflow Engine for Phase 2

Executes multi-step plans with dependency resolution, progress tracking,
checkpointing, and rollback capabilities.
"""

import asyncio
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime
from enum import Enum

from plan import Plan, PlanStep, StepStatus
from tool_executor import ToolExecutor


class WorkflowStatus(Enum):
    """Status of the workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class Checkpoint:
    """Represents a checkpoint in workflow execution"""

    def __init__(self, step_id: str, backup_dir: Optional[Path] = None):
        self.step_id = step_id
        self.timestamp = datetime.now()
        self.backup_dir = backup_dir
        self.state_snapshot: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "timestamp": self.timestamp.isoformat(),
            "backup_dir": str(self.backup_dir) if self.backup_dir else None,
            "state_snapshot": self.state_snapshot
        }


class WorkflowEngine:
    """
    Executes workflow plans with progress tracking and error handling.

    Features:
    - Sequential execution with dependency resolution
    - Checkpointing before risky operations
    - Rollback on failure
    - Progress callbacks
    - Pause/resume capability
    - Retry logic for failed steps
    """

    def __init__(
        self,
        tool_executor: ToolExecutor,
        agent_manager: Optional[Any] = None,
        checkpoint_dir: Optional[Path] = None,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize the workflow engine.

        Args:
            tool_executor: ToolExecutor instance for running tools
            agent_manager: AgentManager instance for spawning agents
            checkpoint_dir: Directory for storing checkpoints/backups
            progress_callback: Function called on progress updates
                             Signature: callback(step_id, status, message)
        """
        self.tool_executor = tool_executor
        self.agent_manager = agent_manager
        self.checkpoint_dir = checkpoint_dir or Path("./workflow_checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.progress_callback = progress_callback

        self.logger = logging.getLogger('WorkflowEngine')

        # Workflow state
        self.current_plan: Optional[Plan] = None
        self.status = WorkflowStatus.PENDING
        self.checkpoints: List[Checkpoint] = []
        self.execution_log: List[Dict[str, Any]] = []

        # Control flags
        self.pause_requested = False
        self.cancel_requested = False

        # Statistics
        self.steps_completed = 0
        self.steps_failed = 0
        self.total_execution_time = 0.0

    def _report_progress(self, step_id: str, status: str, message: str):
        """Report progress via callback"""
        if self.progress_callback:
            try:
                self.progress_callback(step_id, status, message)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {e}")

        # Log progress
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "step_id": step_id,
            "status": status,
            "message": message
        })

    def _create_checkpoint(self, step: PlanStep) -> Checkpoint:
        """
        Create a checkpoint before executing a step.

        For file operations, backs up files that might be modified.
        """
        self.logger.info(f"Creating checkpoint for step {step.step_id}")

        checkpoint = Checkpoint(step.step_id)

        # If this step writes files, create a backup
        if step.tool == "write_file_tool" and step.arguments.get("path"):
            file_path = Path(step.arguments["path"])

            if file_path.exists():
                # Create backup directory for this checkpoint
                backup_dir = self.checkpoint_dir / f"checkpoint_{step.step_id}_{int(datetime.now().timestamp())}"
                backup_dir.mkdir(parents=True, exist_ok=True)

                # Backup the file
                backup_path = backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)

                checkpoint.backup_dir = backup_dir
                checkpoint.state_snapshot["original_path"] = str(file_path)
                checkpoint.state_snapshot["backup_path"] = str(backup_path)

                self.logger.info(f"Created backup at {backup_path}")

        self.checkpoints.append(checkpoint)
        return checkpoint

    def _rollback_to_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """
        Rollback to a specific checkpoint.

        Restores files from backup if they were modified.
        """
        self.logger.info(f"Rolling back to checkpoint for step {checkpoint.step_id}")

        try:
            # Restore backed up files
            if checkpoint.backup_dir and checkpoint.backup_dir.exists():
                backup_path = Path(checkpoint.state_snapshot.get("backup_path", ""))
                original_path = Path(checkpoint.state_snapshot.get("original_path", ""))

                if backup_path.exists() and original_path:
                    shutil.copy2(backup_path, original_path)
                    self.logger.info(f"Restored {original_path} from backup")

            return True

        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False

    def _rollback_all(self):
        """Rollback all checkpoints in reverse order"""
        self.logger.info(f"Rolling back {len(self.checkpoints)} checkpoints")

        for checkpoint in reversed(self.checkpoints):
            self._rollback_to_checkpoint(checkpoint)

        self.status = WorkflowStatus.ROLLED_BACK
        self._report_progress("workflow", "rolled_back", "All changes rolled back")

    async def _execute_tool(self, step: PlanStep) -> Tuple[bool, Any, str]:
        """
        Execute a tool for a step.

        Returns:
            Tuple of (success, result, error_message)
        """
        if not step.tool:
            return (True, None, "")

        tool_name = step.tool
        args = step.arguments or {}

        self.logger.info(f"Executing tool: {tool_name} with args: {args}")

        try:
            if tool_name == "execute_bash":
                command = args.get("command", "")
                result = await self.tool_executor.execute_bash(command)
                return (result.success, result.stdout, result.stderr or result.error_message or "")

            elif tool_name == "execute_python_script":
                code = args.get("code", "")
                result = await self.tool_executor.execute_python_script(code)
                return (result.success, result.stdout, result.stderr or result.error_message or "")

            elif tool_name == "read_file_tool":
                path = args.get("path", "")
                result = await self.tool_executor.read_file(Path(path) if isinstance(path, str) else path)
                return (result.success, result.stdout, result.error_message or "")

            elif tool_name == "write_file_tool":
                path = args.get("path", "")
                content = args.get("content", "")
                result = await self.tool_executor.write_file(
                    Path(path) if isinstance(path, str) else path,
                    content
                )
                return (result.success, result.stdout, result.error_message or "")

            elif tool_name == "list_files_tool":
                path = args.get("path", ".")
                pattern = args.get("pattern", "*")
                result = await self.tool_executor.list_files(
                    Path(path) if isinstance(path, str) else path,
                    pattern
                )
                return (result.success, result.stdout, result.error_message or "")

            else:
                return (False, None, f"Unknown tool: {tool_name}")

        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return (False, None, str(e))

    async def _execute_step(
        self,
        step: PlanStep,
        retry_count: int = 0,
        max_retries: int = 2
    ) -> bool:
        """
        Execute a single step.

        Args:
            step: The step to execute
            retry_count: Current retry attempt
            max_retries: Maximum number of retries

        Returns:
            True if step succeeded, False otherwise
        """
        self.logger.info(f"Executing step {step.step_id}: {step.description}")

        # Update step status
        step.status = StepStatus.IN_PROGRESS
        step.start_time = datetime.now()
        self._report_progress(step.step_id, "in_progress", step.description)

        try:
            # Create checkpoint before risky operations
            if step.tool in ["write_file_tool", "execute_bash"]:
                self._create_checkpoint(step)

            # Execute the tool
            if step.tool:
                success, result, error = await self._execute_tool(step)

                if not success:
                    raise Exception(error or "Tool execution failed")

                step.result = result
            else:
                # No tool specified - this might be a manual step or agent task
                # For now, we'll mark it as successful
                step.result = "Completed (no tool specified)"

            # Mark as completed
            step.status = StepStatus.COMPLETED
            step.end_time = datetime.now()
            self.steps_completed += 1

            execution_time = (step.end_time - step.start_time).total_seconds()
            self.total_execution_time += execution_time

            self._report_progress(
                step.step_id,
                "completed",
                f"Completed in {execution_time:.2f}s"
            )

            return True

        except Exception as e:
            self.logger.error(f"Error executing step {step.step_id}: {e}")

            # Retry logic
            if retry_count < max_retries:
                self.logger.info(f"Retrying step {step.step_id} (attempt {retry_count + 1}/{max_retries})")
                step.status = StepStatus.PENDING
                await asyncio.sleep(1)  # Brief delay before retry
                return await self._execute_step(step, retry_count + 1, max_retries)

            # Max retries exceeded
            step.status = StepStatus.FAILED
            step.end_time = datetime.now()
            step.error = str(e)
            self.steps_failed += 1

            self._report_progress(step.step_id, "failed", str(e))

            return False

    async def execute_plan(
        self,
        plan: Plan,
        auto_rollback: bool = True,
        stop_on_error: bool = True
    ) -> Tuple[bool, str]:
        """
        Execute a workflow plan.

        Args:
            plan: The Plan to execute
            auto_rollback: Whether to rollback on failure
            stop_on_error: Whether to stop execution on first error

        Returns:
            Tuple of (success, message)
        """
        self.logger.info(f"Starting execution of plan: {plan.name}")

        # Validate plan
        is_valid, errors = plan.validate()
        if not is_valid:
            error_msg = "Plan validation failed: " + "; ".join(errors)
            self.logger.error(error_msg)
            return (False, error_msg)

        # Check approval
        if not plan.approved:
            return (False, "Plan not approved by user")

        # Initialize execution
        self.current_plan = plan
        self.status = WorkflowStatus.RUNNING
        self.checkpoints = []
        self.execution_log = []
        self.steps_completed = 0
        self.steps_failed = 0
        self.total_execution_time = 0.0

        self._report_progress("workflow", "started", f"Executing plan: {plan.name}")

        try:
            # Get execution order (respects dependencies)
            steps_ordered = plan.get_execution_order()

            # Execute steps in order
            for step in steps_ordered:
                # Check for pause/cancel
                if self.pause_requested:
                    self.status = WorkflowStatus.PAUSED
                    return (False, "Execution paused by user")

                if self.cancel_requested:
                    if auto_rollback:
                        self._rollback_all()
                    return (False, "Execution canceled by user")

                # Execute the step
                success = await self._execute_step(step)

                if not success and stop_on_error:
                    self.logger.error(f"Step {step.step_id} failed, stopping execution")

                    if auto_rollback:
                        self._rollback_all()
                        return (False, f"Step failed: {step.description}. Changes rolled back.")

                    self.status = WorkflowStatus.FAILED
                    return (False, f"Step failed: {step.description}")

            # All steps completed
            self.status = WorkflowStatus.COMPLETED
            self._report_progress("workflow", "completed", f"Plan completed successfully")

            summary = f"Completed {self.steps_completed}/{len(plan.steps)} steps in {self.total_execution_time:.2f}s"
            return (True, summary)

        except Exception as e:
            self.logger.error(f"Error during plan execution: {e}")
            self.status = WorkflowStatus.FAILED

            if auto_rollback:
                self._rollback_all()
                return (False, f"Execution failed: {e}. Changes rolled back.")

            return (False, f"Execution failed: {e}")

    def pause(self):
        """Request to pause execution"""
        self.pause_requested = True
        self.logger.info("Pause requested")

    def resume(self):
        """Resume paused execution"""
        self.pause_requested = False
        self.logger.info("Execution resumed")

    def cancel(self):
        """Request to cancel execution"""
        self.cancel_requested = True
        self.logger.info("Cancel requested")

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the current execution"""
        if not self.current_plan:
            return {"status": "no_plan"}

        completed, total = self.current_plan.get_progress()

        return {
            "plan_id": self.current_plan.plan_id,
            "plan_name": self.current_plan.name,
            "status": self.status.value,
            "steps_completed": completed,
            "steps_total": total,
            "steps_failed": self.steps_failed,
            "progress_percentage": self.current_plan.get_progress_percentage(),
            "total_execution_time": self.total_execution_time,
            "checkpoints_created": len(self.checkpoints)
        }

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get the execution log"""
        return self.execution_log.copy()

    def save_state(self, file_path: Path):
        """Save the current workflow state to a file"""
        if not self.current_plan:
            raise ValueError("No plan to save")

        state = {
            "plan": self.current_plan.to_dict(),
            "status": self.status.value,
            "summary": self.get_execution_summary(),
            "log": self.execution_log
        }

        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)

        self.logger.info(f"Workflow state saved to {file_path}")

    @classmethod
    def load_state(cls, file_path: Path, tool_executor: ToolExecutor) -> 'WorkflowEngine':
        """Load a workflow state from a file"""
        with open(file_path, 'r') as f:
            state = json.load(f)

        engine = cls(tool_executor)
        engine.current_plan = Plan.from_dict(state["plan"])
        engine.status = WorkflowStatus(state["status"])
        engine.execution_log = state.get("log", [])

        return engine
