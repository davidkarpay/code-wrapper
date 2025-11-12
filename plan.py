"""
Plan Data Structure for Phase 2 Workflow Engine

This module defines the Plan and PlanStep classes used by the workflow engine
to represent multi-step execution plans with dependencies and progress tracking.
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime


class StepStatus(Enum):
    """Status of a plan step"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep:
    """
    Represents a single step in a workflow plan.

    Attributes:
        step_id: Unique identifier for this step
        description: Human-readable description of what this step does
        agent_id: Which agent should execute this step (main, reviewer, etc.)
        tool: Optional tool to execute (execute_bash, write_file, etc.)
        arguments: Optional arguments for the tool
        dependencies: List of step_ids this step depends on
        estimated_time: Estimated execution time in seconds
        status: Current status of the step
        result: Result/output from step execution
        error: Error message if step failed
        start_time: When execution started
        end_time: When execution completed
    """

    def __init__(
        self,
        description: str,
        agent_id: str = "main",
        tool: Optional[str] = None,
        arguments: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        estimated_time: int = 30,
        step_id: Optional[str] = None
    ):
        self.step_id = step_id or str(uuid.uuid4())[:8]
        self.description = description
        self.agent_id = agent_id
        self.tool = tool
        self.arguments = arguments or {}
        self.dependencies = dependencies or []
        self.estimated_time = estimated_time
        self.status = StepStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize step to dictionary"""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "agent_id": self.agent_id,
            "tool": self.tool,
            "arguments": self.arguments,
            "dependencies": self.dependencies,
            "estimated_time": self.estimated_time,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanStep':
        """Deserialize step from dictionary"""
        step = cls(
            description=data["description"],
            agent_id=data.get("agent_id", "main"),
            tool=data.get("tool"),
            arguments=data.get("arguments"),
            dependencies=data.get("dependencies"),
            estimated_time=data.get("estimated_time", 30),
            step_id=data.get("step_id")
        )
        step.status = StepStatus(data.get("status", "pending"))
        step.result = data.get("result")
        step.error = data.get("error")

        if data.get("start_time"):
            step.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            step.end_time = datetime.fromisoformat(data["end_time"])

        return step

    def __repr__(self) -> str:
        return f"PlanStep(id={self.step_id}, desc='{self.description[:30]}...', status={self.status.value})"


class Plan:
    """
    Represents a complete workflow plan with multiple steps.

    Attributes:
        plan_id: Unique identifier for this plan
        name: Short name for the plan
        description: Detailed description of what the plan does
        steps: List of PlanStep objects
        created_at: When the plan was created
        approved: Whether user has approved this plan
        total_estimated_time: Total estimated execution time
        metadata: Additional metadata (cost estimates, etc.)
    """

    def __init__(
        self,
        name: str,
        description: str,
        steps: Optional[List[PlanStep]] = None,
        plan_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.plan_id = plan_id or str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.steps = steps or []
        self.created_at = datetime.now()
        self.approved = False
        self.metadata = metadata or {}

    def add_step(self, step: PlanStep) -> None:
        """Add a step to the plan"""
        self.steps.append(step)

    def get_step(self, step_id: str) -> Optional[PlanStep]:
        """Get a step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_total_estimated_time(self) -> int:
        """Calculate total estimated time in seconds"""
        return sum(step.estimated_time for step in self.steps)

    def get_progress(self) -> Tuple[int, int]:
        """Get progress as (completed, total) tuple"""
        completed = sum(1 for step in self.steps if step.status == StepStatus.COMPLETED)
        return (completed, len(self.steps))

    def get_progress_percentage(self) -> float:
        """Get progress as percentage"""
        if not self.steps:
            return 0.0
        completed, total = self.get_progress()
        return (completed / total) * 100

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate plan structure and dependencies.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for empty plan
        if not self.steps:
            errors.append("Plan has no steps")
            return (False, errors)

        # Collect all step IDs
        step_ids = {step.step_id for step in self.steps}

        # Validate each step
        for i, step in enumerate(self.steps):
            # Check step ID uniqueness
            if list(s.step_id for s in self.steps).count(step.step_id) > 1:
                errors.append(f"Step {i+1}: Duplicate step ID '{step.step_id}'")

            # Validate dependencies exist
            for dep in step.dependencies:
                if dep not in step_ids:
                    errors.append(f"Step {i+1}: Dependency '{dep}' not found")

            # Check for circular dependencies
            if self._has_circular_dependency(step.step_id):
                errors.append(f"Step {i+1}: Circular dependency detected")

            # Validate agent_id
            valid_agents = ["main", "reviewer", "researcher", "implementer", "tester", "optimizer"]
            if step.agent_id not in valid_agents:
                errors.append(f"Step {i+1}: Invalid agent_id '{step.agent_id}'")

            # Validate tool if specified
            if step.tool:
                valid_tools = ["execute_bash", "execute_python_script", "read_file_tool",
                              "write_file_tool", "list_files_tool"]
                if step.tool not in valid_tools:
                    errors.append(f"Step {i+1}: Invalid tool '{step.tool}'")

        return (len(errors) == 0, errors)

    def _has_circular_dependency(self, step_id: str, visited: Optional[set] = None) -> bool:
        """Check if a step has circular dependencies"""
        if visited is None:
            visited = set()

        if step_id in visited:
            return True

        visited.add(step_id)
        step = self.get_step(step_id)

        if step:
            for dep in step.dependencies:
                if self._has_circular_dependency(dep, visited.copy()):
                    return True

        return False

    def get_execution_order(self) -> List[PlanStep]:
        """
        Get steps in execution order, respecting dependencies.
        Uses topological sort.
        """
        # Build dependency graph
        in_degree = {step.step_id: len(step.dependencies) for step in self.steps}

        # Find steps with no dependencies
        queue = [step for step in self.steps if len(step.dependencies) == 0]
        result = []

        while queue:
            # Get next step with all dependencies satisfied
            current = queue.pop(0)
            result.append(current)

            # Update dependent steps
            for step in self.steps:
                if current.step_id in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step)

        # If we didn't process all steps, there's a circular dependency
        if len(result) != len(self.steps):
            raise ValueError("Circular dependency detected in plan")

        return result

    def estimate_cost(self, model_costs: Optional[Dict[str, float]] = None) -> float:
        """
        Estimate API cost for executing this plan.

        Args:
            model_costs: Dict mapping agent_id to cost per request
                        Default: {"main": 0.10, "others": 0.02}

        Returns:
            Estimated cost in dollars
        """
        if model_costs is None:
            model_costs = {
                "main": 0.10,  # 120b model
                "reviewer": 0.02,
                "researcher": 0.02,
                "implementer": 0.02,
                "tester": 0.02,
                "optimizer": 0.02
            }

        total_cost = 0.0
        for step in self.steps:
            cost = model_costs.get(step.agent_id, 0.02)
            total_cost += cost

        return total_cost

    def to_dict(self) -> Dict[str, Any]:
        """Serialize plan to dictionary"""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at.isoformat(),
            "approved": self.approved,
            "metadata": self.metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize plan to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plan':
        """Deserialize plan from dictionary"""
        steps = [PlanStep.from_dict(s) for s in data.get("steps", [])]

        plan = cls(
            name=data["name"],
            description=data["description"],
            steps=steps,
            plan_id=data.get("plan_id"),
            metadata=data.get("metadata")
        )

        if data.get("created_at"):
            plan.created_at = datetime.fromisoformat(data["created_at"])

        plan.approved = data.get("approved", False)

        return plan

    @classmethod
    def from_json(cls, json_str: str) -> 'Plan':
        """Deserialize plan from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def display(self, show_details: bool = True) -> str:
        """
        Generate a formatted display string for the plan.

        Args:
            show_details: Whether to show full details or summary only

        Returns:
            Formatted string representation
        """
        output = []
        output.append("=" * 70)
        output.append(f"PLAN: {self.name} (ID: {self.plan_id})")
        output.append("=" * 70)
        output.append(f"\nDescription: {self.description}")
        output.append(f"\nSteps: {len(self.steps)}")
        output.append(f"Estimated Time: {self.get_total_estimated_time()}s ({self.get_total_estimated_time()//60}m {self.get_total_estimated_time()%60}s)")
        output.append(f"Estimated Cost: ${self.estimate_cost():.4f}")
        output.append(f"Status: {'APPROVED' if self.approved else 'PENDING APPROVAL'}")

        completed, total = self.get_progress()
        output.append(f"Progress: {completed}/{total} ({self.get_progress_percentage():.1f}%)")

        if show_details:
            output.append("\n" + "-" * 70)
            output.append("STEPS:")
            output.append("-" * 70)

            for i, step in enumerate(self.steps, 1):
                status_icon = {
                    StepStatus.PENDING: "○",
                    StepStatus.IN_PROGRESS: "⟳",
                    StepStatus.COMPLETED: "✓",
                    StepStatus.FAILED: "✗",
                    StepStatus.SKIPPED: "⊘"
                }.get(step.status, "?")

                output.append(f"\n{status_icon} Step {i} [{step.step_id}]: {step.description}")
                output.append(f"   Agent: {step.agent_id} | Time: ~{step.estimated_time}s")

                if step.tool:
                    output.append(f"   Tool: {step.tool}")

                if step.dependencies:
                    deps_str = ", ".join(step.dependencies)
                    output.append(f"   Dependencies: {deps_str}")

                if step.error:
                    output.append(f"   Error: {step.error}")

        output.append("\n" + "=" * 70)

        return "\n".join(output)

    def __repr__(self) -> str:
        return f"Plan(id={self.plan_id}, name='{self.name}', steps={len(self.steps)})"
