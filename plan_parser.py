"""
Plan Parser - Extracts and parses workflow plans from agent responses

Parses [PLAN]...[/PLAN] tags in agent outputs and converts them to Plan objects.
"""

import re
import logging
from typing import Optional, List, Tuple, Dict, Any

from plan import Plan, PlanStep


class PlanParser:
    """Parses workflow plans from agent responses"""

    def __init__(self):
        self.logger = logging.getLogger('PlanParser')

        # Regex patterns
        self.plan_pattern = re.compile(
            r'\[PLAN\](.*?)\[/PLAN\]',
            re.DOTALL | re.IGNORECASE
        )

        self.workflow_pattern = re.compile(
            r'##\s*Workflow:\s*(.+)',
            re.IGNORECASE
        )

        self.step_pattern = re.compile(
            r'###\s*Step\s*\d+:\s*(.+?)(?=###|##|$)',
            re.DOTALL | re.IGNORECASE
        )

    def extract_plan_text(self, text: str) -> Optional[str]:
        """
        Extract [PLAN]...[/PLAN] content from text.

        Args:
            text: Agent response text

        Returns:
            Plan content if found, None otherwise
        """
        match = self.plan_pattern.search(text)
        if match:
            return match.group(1).strip()
        return None

    def parse_plan(self, text: str) -> Optional[Plan]:
        """
        Parse a full workflow plan from agent response.

        Args:
            text: Agent response containing [PLAN]...[/PLAN] tags

        Returns:
            Parsed Plan object, or None if parsing fails
        """
        # Extract plan content
        plan_content = self.extract_plan_text(text)

        if not plan_content:
            self.logger.debug("No [PLAN] tags found in text")
            return None

        try:
            # Check if it's a workflow plan or simple file operation plan
            if "###" in plan_content and "Step" in plan_content:
                return self._parse_workflow_plan(plan_content)
            else:
                # Simple file operation plan - not a workflow
                self.logger.debug("Found file operation plan, not a workflow plan")
                return None

        except Exception as e:
            self.logger.error(f"Error parsing plan: {e}")
            return None

    def _parse_workflow_plan(self, plan_text: str) -> Optional[Plan]:
        """
        Parse a workflow-style plan with steps.

        Expected format:
        ## Workflow: [name]

        ### Step 1: [description]
        - Agent: [agent_id]
        - Tool: [tool_name]
        - Arguments: [JSON or description]
        - Dependencies: [step references]
        - Estimated Time: [time]

        ### Step 2: ...
        """
        lines = plan_text.split('\n')

        # Extract workflow name
        workflow_match = self.workflow_pattern.search(plan_text)
        workflow_name = workflow_match.group(1).strip() if workflow_match else "Unnamed Workflow"

        # Extract description (text between workflow name and first step)
        description_lines = []
        in_description = False
        for line in lines:
            if line.strip().startswith("## Workflow"):
                in_description = True
                continue
            if line.strip().startswith("###"):
                break
            if in_description and line.strip():
                description_lines.append(line.strip())

        description = " ".join(description_lines) if description_lines else workflow_name

        # Parse steps
        steps = []
        step_matches = self.step_pattern.finditer(plan_text)

        for step_num, step_match in enumerate(step_matches, 1):
            step_text = step_match.group(0).strip()
            step = self._parse_step(step_text, step_num)

            if step:
                steps.append(step)

        if not steps:
            self.logger.warning("No steps found in workflow plan")
            return None

        # Fix dependencies: map "Step N" references to actual step IDs
        step_num_to_id = {i+1: step.step_id for i, step in enumerate(steps)}

        for step in steps:
            fixed_dependencies = []
            for dep in step.dependencies:
                if dep.startswith("step_"):
                    # Extract step number
                    try:
                        step_num = int(dep.split("_")[1])
                        if step_num in step_num_to_id:
                            fixed_dependencies.append(step_num_to_id[step_num])
                    except (ValueError, IndexError):
                        fixed_dependencies.append(dep)  # Keep as-is if can't parse
                else:
                    fixed_dependencies.append(dep)
            step.dependencies = fixed_dependencies

        # Extract metadata (total time, cost)
        metadata = self._extract_metadata(plan_text)

        # Create plan
        plan = Plan(
            name=workflow_name,
            description=description,
            steps=steps,
            metadata=metadata
        )

        self.logger.info(f"Parsed workflow plan: {workflow_name} with {len(steps)} steps")

        return plan

    def _parse_step(self, step_text: str, step_num: int) -> Optional[PlanStep]:
        """Parse a single step from text"""
        lines = step_text.split('\n')

        # Extract step description from header
        header_match = re.search(r'###\s*Step\s*\d+:\s*(.+)', lines[0])
        description = header_match.group(1).strip() if header_match else f"Step {step_num}"

        # Parse step properties
        agent_id = "main"
        tool = None
        arguments = {}
        dependencies = []
        estimated_time = 30

        for line in lines[1:]:
            line = line.strip()

            # Parse agent
            if line.startswith("- Agent:") or line.startswith("Agent:"):
                agent_text = line.split(":", 1)[1].strip()
                # Extract just the agent name
                agent_id = re.split(r'[/\s\[\(]', agent_text)[0].strip().lower()

            # Parse tool
            elif line.startswith("- Tool:") or line.startswith("Tool:"):
                tool_text = line.split(":", 1)[1].strip()
                tool = tool_text.split()[0] if tool_text else None

            # Parse arguments
            elif line.startswith("- Arguments:") or line.startswith("Arguments:"):
                args_text = line.split(":", 1)[1].strip()
                arguments = self._parse_arguments(args_text)

            # Parse dependencies
            elif line.startswith("- Dependencies:") or line.startswith("Dependencies:"):
                deps_text = line.split(":", 1)[1].strip()
                dependencies = self._parse_dependencies(deps_text)

            # Parse estimated time
            elif line.startswith("- Estimated Time:") or line.startswith("Estimated Time:"):
                time_text = line.split(":", 1)[1].strip()
                estimated_time = self._parse_time(time_text)

        # Create step
        step = PlanStep(
            description=description,
            agent_id=agent_id,
            tool=tool,
            arguments=arguments,
            dependencies=dependencies,
            estimated_time=estimated_time
        )

        return step

    def _parse_arguments(self, args_text: str) -> Dict[str, Any]:
        """Parse arguments from text"""
        # Try to parse as JSON
        if args_text.startswith("{"):
            try:
                import json
                return json.loads(args_text)
            except:
                pass

        # Parse as key-value pairs
        arguments = {}

        # Look for {"key": "value"} pattern
        kv_pattern = re.findall(r'"(\w+)":\s*"([^"]+)"', args_text)
        for key, value in kv_pattern:
            arguments[key] = value

        return arguments

    def _parse_dependencies(self, deps_text: str) -> List[str]:
        """Parse dependencies from text"""
        if "none" in deps_text.lower():
            return []

        # Extract step numbers or IDs
        dependencies = []

        # Look for "Step N" pattern
        step_refs = re.findall(r'Step\s+(\d+)', deps_text, re.IGNORECASE)
        for step_ref in step_refs:
            dependencies.append(f"step_{step_ref}")

        # Look for explicit IDs
        id_refs = re.findall(r'\b([a-f0-9]{8})\b', deps_text)
        dependencies.extend(id_refs)

        return dependencies

    def _parse_time(self, time_text: str) -> int:
        """Parse estimated time to seconds"""
        time_text = time_text.lower()

        # Extract number
        number_match = re.search(r'(\d+)', time_text)
        if not number_match:
            return 30

        value = int(number_match.group(1))

        # Check unit
        if 'min' in time_text or 'm' in time_text:
            return value * 60
        elif 'hour' in time_text or 'h' in time_text:
            return value * 3600
        else:
            # Assume seconds
            return value

    def _extract_metadata(self, plan_text: str) -> Dict[str, Any]:
        """Extract metadata from plan text"""
        metadata = {}

        # Total estimated time
        time_match = re.search(r'Total Estimated Time:\s*(.+)', plan_text, re.IGNORECASE)
        if time_match:
            metadata['total_time'] = time_match.group(1).strip()

        # Cost estimate
        cost_match = re.search(r'Cost Estimate:\s*\$?([\d.]+)', plan_text, re.IGNORECASE)
        if cost_match:
            metadata['estimated_cost'] = float(cost_match.group(1))

        return metadata

    def has_plan(self, text: str) -> bool:
        """Check if text contains a [PLAN] tag"""
        return bool(self.plan_pattern.search(text))
