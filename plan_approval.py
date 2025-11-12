"""
Plan Approval Workflow - Interactive user approval for workflow plans

Handles displaying plans to users and getting approval/rejection/modification.
"""

import logging
from typing import Optional, Tuple, List
from datetime import datetime

from plan import Plan, PlanStep
from output_manager import OutputManager


class PlanApprovalUI:
    """Interactive UI for plan approval"""

    def __init__(self, output_manager: Optional[OutputManager] = None):
        """
        Initialize the plan approval UI.

        Args:
            output_manager: OutputManager for formatted output
        """
        self.output_manager = output_manager
        self.logger = logging.getLogger('PlanApprovalUI')

    def _print(self, text: str, agent_id: str = "system", style: str = "normal"):
        """Print text using output manager or standard print"""
        if self.output_manager:
            self.output_manager.print(agent_id, text, style=style)
        else:
            print(text)

    def display_plan(self, plan: Plan):
        """Display a formatted plan to the user"""
        self._print("\n" + "=" * 70, "system", "bold")
        self._print(f"  WORKFLOW PLAN: {plan.name}", "system", "bold")
        self._print("=" * 70, "system", "bold")

        self._print(f"\nDescription: {plan.description}", "system")
        self._print(f"\nPlan ID: {plan.plan_id}", "system", "dim")

        # Summary
        self._print(f"\n📊 Summary:", "system", "bold")
        self._print(f"   Steps: {len(plan.steps)}", "system")

        total_time = plan.get_total_estimated_time()
        minutes = total_time // 60
        seconds = total_time % 60
        self._print(f"   Estimated Time: {minutes}m {seconds}s", "system")

        cost = plan.estimate_cost()
        self._print(f"   Estimated Cost: ${cost:.4f}", "system")

        # Steps
        self._print(f"\n📝 Execution Steps:", "system", "bold")
        self._print("-" * 70, "system")

        for i, step in enumerate(plan.steps, 1):
            self._print(f"\n○ Step {i} [{step.step_id}]: {step.description}", "system", "bold")
            self._print(f"   Agent: {step.agent_id}", "system")

            if step.tool:
                self._print(f"   Tool: {step.tool}", "system")

                if step.arguments:
                    args_str = ", ".join(f"{k}={v}" for k, v in list(step.arguments.items())[:2])
                    if len(step.arguments) > 2:
                        args_str += ", ..."
                    self._print(f"   Arguments: {args_str}", "system", "dim")

            if step.dependencies:
                deps_str = ", ".join(step.dependencies)
                self._print(f"   Dependencies: {deps_str}", "system", "dim")

            self._print(f"   Time: ~{step.estimated_time}s", "system")

        self._print("\n" + "=" * 70, "system")

    def request_approval(self, plan: Plan) -> Tuple[str, Optional[str]]:
        """
        Display plan and request user approval.

        Returns:
            Tuple of (decision, modification_request)
            decision: "approve", "reject", or "modify"
            modification_request: User's modification request if decision is "modify"
        """
        # Display the plan
        self.display_plan(plan)

        # Validation warnings
        is_valid, errors = plan.validate()
        if not is_valid:
            self._print("\n⚠️  VALIDATION WARNINGS:", "system", "warning")
            for error in errors:
                self._print(f"   • {error}", "system", "warning")
            self._print("", "system")

        # Prompt for approval
        self._print("\n" + "=" * 70, "system")
        self._print("  APPROVAL REQUIRED", "system", "bold")
        self._print("=" * 70, "system")

        self._print("\nOptions:", "system")
        self._print("  [A] Approve - Execute this plan", "system")
        self._print("  [R] Reject - Cancel this plan", "system")
        self._print("  [M] Modify - Request changes to the plan", "system")
        self._print("  [V] View - Display plan details again", "system")
        self._print("", "system")

        while True:
            try:
                response = input("Your decision [A/R/M/V]: ").strip().upper()

                if response == 'A' or response == 'APPROVE':
                    plan.approved = True
                    self._print("\n✓ Plan approved for execution", "system", "success")
                    return ("approve", None)

                elif response == 'R' or response == 'REJECT':
                    self._print("\n✗ Plan rejected", "system", "error")
                    return ("reject", None)

                elif response == 'M' or response == 'MODIFY':
                    self._print("\nWhat changes would you like to the plan?", "system")
                    self._print("(Describe your requested modifications):", "system")
                    modification = input("> ").strip()

                    if modification:
                        self._print(f"\n📝 Modification request recorded", "system")
                        return ("modify", modification)
                    else:
                        self._print("No modification provided, please try again.", "system")

                elif response == 'V' or response == 'VIEW':
                    self.display_plan(plan)

                else:
                    self._print(f"Invalid option: '{response}'. Please choose A, R, M, or V.", "system", "warning")

            except KeyboardInterrupt:
                self._print("\n\n✗ Plan approval interrupted", "system", "error")
                return ("reject", None)

            except Exception as e:
                self.logger.error(f"Error during approval: {e}")
                self._print(f"Error: {e}", "system", "error")
                return ("reject", None)

    def confirm_execution(self, plan: Plan) -> bool:
        """
        Final confirmation before execution.

        Returns:
            True if user confirms, False otherwise
        """
        self._print("\n" + "-" * 70, "system")
        self._print("⚠️  FINAL CONFIRMATION", "system", "warning")
        self._print("-" * 70, "system")

        self._print(f"\nAbout to execute: {plan.name}", "system", "bold")
        self._print(f"Steps: {len(plan.steps)}", "system")

        # Warn about file operations
        file_write_steps = sum(1 for s in plan.steps if s.tool == "write_file_tool")
        bash_steps = sum(1 for s in plan.steps if s.tool == "execute_bash")

        if file_write_steps > 0:
            self._print(f"⚠️  Will modify {file_write_steps} file(s)", "system", "warning")

        if bash_steps > 0:
            self._print(f"⚠️  Will execute {bash_steps} bash command(s)", "system", "warning")

        self._print("\nContinue with execution?", "system")

        try:
            response = input("[Y/N]: ").strip().upper()

            if response == 'Y' or response == 'YES':
                self._print("✓ Execution confirmed", "system", "success")
                return True
            else:
                self._print("✗ Execution canceled", "system", "error")
                return False

        except KeyboardInterrupt:
            self._print("\n✗ Execution canceled", "system", "error")
            return False

    def display_progress(self, step_id: str, status: str, message: str):
        """
        Display progress update during execution.

        Args:
            step_id: ID of the step
            status: Status (in_progress, completed, failed, etc.)
            message: Progress message
        """
        status_icons = {
            "in_progress": "⟳",
            "completed": "✓",
            "failed": "✗",
            "pending": "○",
            "skipped": "⊘"
        }

        status_styles = {
            "in_progress": "info",
            "completed": "success",
            "failed": "error",
            "pending": "dim",
            "skipped": "dim"
        }

        icon = status_icons.get(status, "•")
        style = status_styles.get(status, "normal")

        timestamp = datetime.now().strftime("%H:%M:%S")

        if status == "in_progress":
            self._print(f"[{timestamp}] {icon} {message}...", "workflow", style)
        elif status == "completed":
            self._print(f"[{timestamp}] {icon} {message}", "workflow", style)
        elif status == "failed":
            self._print(f"[{timestamp}] {icon} FAILED: {message}", "workflow", style)
        else:
            self._print(f"[{timestamp}] {icon} {message}", "workflow", style)

    def display_execution_summary(self, summary: dict):
        """Display execution summary after completion"""
        self._print("\n" + "=" * 70, "system", "bold")
        self._print("  EXECUTION SUMMARY", "system", "bold")
        self._print("=" * 70, "system", "bold")

        status = summary.get("status", "unknown")
        steps_completed = summary.get("steps_completed", 0)
        steps_total = summary.get("steps_total", 0)
        steps_failed = summary.get("steps_failed", 0)
        execution_time = summary.get("total_execution_time", 0)

        self._print(f"\nPlan: {summary.get('plan_name', 'Unknown')}", "system")
        self._print(f"Status: {status.upper()}", "system",
                   "success" if status == "completed" else "error")

        self._print(f"\nProgress: {steps_completed}/{steps_total} steps completed", "system")
        if steps_failed > 0:
            self._print(f"Failed: {steps_failed} step(s)", "system", "error")

        minutes = int(execution_time // 60)
        seconds = int(execution_time % 60)
        self._print(f"Time: {minutes}m {seconds}s", "system")

        checkpoints = summary.get("checkpoints_created", 0)
        if checkpoints > 0:
            self._print(f"Checkpoints: {checkpoints} created", "system")

        self._print("\n" + "=" * 70, "system")
