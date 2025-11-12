"""
Multi-Agent Orchestrator
Main entry point for running the multi-agent system
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Optional, List
import logging

from agent_manager import AgentManager, AgentRole, AgentStatus
from output_manager import OutputManager
from async_streaming_agent import (
    AsyncStreamingAgent,
    load_multi_agent_config,
    create_agent_from_profile
)
from tool_executor import ToolExecutor
from workflow_engine import WorkflowEngine
from plan_parser import PlanParser
from plan_approval import PlanApprovalUI
from plan import Plan


class MultiAgentOrchestrator:
    """Orchestrates multiple AI agents"""

    def __init__(self, config_file: str = "agent_config_multi_agent.json"):
        """
        Initialize the orchestrator

        Args:
            config_file: Path to multi-agent configuration file
        """
        self.config = load_multi_agent_config(config_file)
        self.output_manager = OutputManager(enable_colors=True)
        self.agent_manager = AgentManager()
        self.tool_executor = ToolExecutor(self.config)

        # Phase 2: Workflow engine components
        self.workflow_engine = WorkflowEngine(
            tool_executor=self.tool_executor,
            agent_manager=self.agent_manager,
            progress_callback=self._on_workflow_progress
        )
        self.plan_parser = PlanParser()
        self.plan_approval = PlanApprovalUI(output_manager=self.output_manager)
        self.pending_plans: Dict[str, Plan] = {}  # Store plans awaiting approval

        self.main_agent: Optional[AsyncStreamingAgent] = None
        self.running_tasks: Dict[str, asyncio.Task] = {}

        # Auto-spawning settings
        self.auto_spawn_enabled = self.config.get("spawning_rules", {}).get("auto_spawn_on_keywords", False)
        self.spawning_keywords = self.config.get("spawning_rules", {}).get("keywords", {})
        self.require_confirmation = self.config.get("spawning_rules", {}).get("require_confirmation", False)

        # Setup logging
        self.logger = logging.getLogger('MultiAgentOrchestrator')
        self.logger.setLevel(logging.INFO)

    async def initialize(self):
        """Initialize the orchestrator and create main agent"""
        self.print_banner()

        # Create main agent
        main_profile = self.config["multi_agent_settings"]["default_main_profile"]
        self.main_agent = create_agent_from_profile(
            profile_name=main_profile,
            config_dict=self.config,
            agent_manager=self.agent_manager,
            output_manager=self.output_manager,
            tool_executor=self.tool_executor,
            parent_id=None,
            task_description="Main orchestration agent"
        )

        print(f"\n✅ Main agent initialized: {self.main_agent.agent_id}")
        print(f"   Model: {self.main_agent.config.model_name}")
        print(f"   Provider: {self.main_agent.config.provider}\n")

    def print_banner(self):
        """Print welcome banner"""
        print("=" * 70)
        print("🤖 MULTI-AGENT AI CODING SYSTEM")
        print("=" * 70)
        print("\nSupports concurrent agents with different models")
        print("Main agent coordinates sub-agents for specialized tasks\n")

    def print_help(self):
        """Print available commands"""
        print("\n" + "=" * 70)
        print("📚 COMMANDS")
        print("=" * 70)
        print("\n🔧 Agent Management:")
        print("  /spawn <role> <task>  - Spawn a sub-agent for a specific task")
        print("                          Roles: reviewer, researcher, implementer,")
        print("                                 tester, optimizer, general")
        print("  /agents               - List all active agents")
        print("  /stop <agent_id>      - Stop a specific sub-agent")
        print("  /stop_all             - Stop all sub-agents")
        print("\n📋 Workflow Plans (Phase 2):")
        print("  /plans                - List all pending plans")
        print("  /approve <plan_id>    - Approve and execute a plan")
        print("  /reject <plan_id>     - Reject a pending plan")
        print("  /plan <plan_id>       - View plan details")
        print("  /cancel_workflow      - Cancel running workflow")
        print("\n💬 Communication:")
        print("  @<agent_id> <message> - Send message to specific agent")
        print("  Regular message       - Send to main agent")
        print("\n⚙️ Configuration:")
        print("  /config               - Show current configuration")
        print("  /stats                - Show agent statistics")
        print("  /stream               - Toggle streaming (main agent)")
        print("  /thinking             - Toggle thinking display (main agent)")
        print("  /auto_spawn           - Toggle automatic sub-agent spawning")
        print("\n💾 Session:")
        print("  /reset                - Reset main agent conversation")
        print("  /help                 - Show this help")
        print("  /exit                 - Exit the system")
        print("=" * 70 + "\n")

    async def spawn_sub_agent(
        self,
        role: str,
        task_description: str,
        profile_name: Optional[str] = None
    ) -> Optional[AsyncStreamingAgent]:
        """
        Spawn a sub-agent for a specific task

        Args:
            role: Role of the sub-agent
            task_description: Description of the task
            profile_name: Optional specific profile to use

        Returns:
            Created agent or None if failed
        """
        try:
            # Determine profile to use
            if profile_name is None:
                profile_name = f"{role}_agent"

            # Check if profile exists
            profiles = self.config.get("agent_profiles", {})
            if profile_name not in profiles:
                self.output_manager.write(
                    "system",
                    f"❌ Profile '{profile_name}' not found. Using default sub-agent profile.\n",
                    flush=True
                )
                profile_name = self.config["multi_agent_settings"]["default_sub_agent_profile"]

            # Create sub-agent
            sub_agent = create_agent_from_profile(
                profile_name=profile_name,
                config_dict=self.config,
                agent_manager=self.agent_manager,
                output_manager=self.output_manager,
                tool_executor=self.tool_executor,
                parent_id=self.main_agent.agent_id,
                task_description=task_description
            )

            print(f"\n✅ Spawned {role} agent: {sub_agent.agent_id}")
            print(f"   Model: {sub_agent.config.model_name}")
            print(f"   Task: {task_description}\n")

            return sub_agent

        except Exception as e:
            print(f"\n❌ Failed to spawn agent: {e}\n")
            self.logger.error(f"Failed to spawn agent: {e}", exc_info=True)
            return None

    async def check_and_auto_spawn(self, user_input: str) -> Optional[List[AsyncStreamingAgent]]:
        """
        Check user input for keywords and auto-spawn appropriate agents

        Args:
            user_input: User's message

        Returns:
            List of spawned agents or None
        """
        if not self.auto_spawn_enabled:
            return None

        # Check for keywords (case-insensitive)
        user_input_lower = user_input.lower()
        spawned_agents = []

        for keyword, profile_name in self.spawning_keywords.items():
            if keyword.lower() in user_input_lower:
                # Ask for confirmation if required
                if self.require_confirmation:
                    print(f"\n🤔 Keyword '{keyword}' detected. Spawn {profile_name}? (y/n): ", end='', flush=True)
                    response = await asyncio.to_thread(input)
                    if response.lower() != 'y':
                        continue

                # Extract role from profile name (e.g., "reviewer_agent" -> "reviewer")
                role = profile_name.replace("_agent", "")

                # Create task description based on keyword context
                task_description = f"Handle {keyword} task: {user_input[:100]}..."

                print(f"\n🚀 Auto-spawning {role} agent (keyword: '{keyword}')...")

                # Spawn the agent
                sub_agent = await self.spawn_sub_agent(role, task_description, profile_name)

                if sub_agent:
                    spawned_agents.append(sub_agent)
                    # Run the task asynchronously
                    task_coro = self.run_agent_task(sub_agent, user_input)
                    task = asyncio.create_task(task_coro)
                    self.running_tasks[sub_agent.agent_id] = task

        return spawned_agents if spawned_agents else None

    async def run_agent_task(
        self,
        agent: AsyncStreamingAgent,
        message: str
    ) -> str:
        """
        Run an agent task asynchronously

        Args:
            agent: Agent to run
            message: Message/task for the agent

        Returns:
            Agent response
        """
        try:
            self.output_manager.print_agent_header(
                agent.agent_id,
                agent.role.value,
                "working"
            )

            response = await agent.process_message_async(message, use_output_manager=True)

            self.output_manager.finalize_agent_output(agent.agent_id)

            # Phase 2: Check for workflow plans in response
            await self.check_for_plan(response)

            return response

        except Exception as e:
            self.logger.error(f"Error running agent {agent.agent_id}: {e}", exc_info=True)
            self.output_manager.write_error(agent.agent_id, str(e))
            return f"Error: {e}"

    def list_agents(self):
        """List all active agents"""
        agents = self.agent_manager.list_agents(include_terminated=False)

        print("\n" + "=" * 70)
        print("🤖 ACTIVE AGENTS")
        print("=" * 70)

        for info in agents:
            status_emoji = self.output_manager._get_status_emoji(info.status.value)
            role_emoji = self.output_manager._get_role_emoji(info.role.value)

            print(f"\n{role_emoji} {info.agent_id}")
            print(f"   Role: {info.role.value}")
            print(f"   Model: {info.model_name}")
            print(f"   Status: {status_emoji} {info.status.value}")

            if info.task_description:
                print(f"   Task: {info.task_description}")

            if info.parent_id:
                print(f"   Parent: {info.parent_id}")

            if info.is_main:
                print("   🌟 MAIN AGENT")

        print("=" * 70 + "\n")

    def show_stats(self):
        """Show system statistics"""
        stats = self.agent_manager.get_statistics()

        print("\n" + "=" * 70)
        print("📊 SYSTEM STATISTICS")
        print("=" * 70)
        print(f"\nTotal Agents: {stats['total_agents']}")
        print(f"Active Agents: {stats['active_agents']}")
        print(f"Main Agent ID: {stats['main_agent_id']}")
        print("\nAgents by Role:")

        for role, count in stats['agents_by_role'].items():
            print(f"  {role}: {count}")

        # Output statistics
        output_stats = self.output_manager.get_statistics()
        print("\nMessage Counts:")
        for agent_id, count in output_stats.items():
            print(f"  {agent_id}: {count}")

        print("=" * 70 + "\n")

    # ===== PHASE 2: WORKFLOW METHODS =====

    def _on_workflow_progress(self, step_id: str, status: str, message: str):
        """Callback for workflow progress updates"""
        self.plan_approval.display_progress(step_id, status, message)

    async def check_for_plan(self, response: str) -> Optional[Plan]:
        """
        Check if agent response contains a workflow plan and handle it.

        Args:
            response: Agent response text

        Returns:
            Parsed Plan if found, None otherwise
        """
        if not self.plan_parser.has_plan(response):
            return None

        # Parse the plan
        plan = self.plan_parser.parse_plan(response)

        if plan:
            self.logger.info(f"Detected workflow plan: {plan.name}")

            # Store the plan
            self.pending_plans[plan.plan_id] = plan

            # Request approval
            print(f"\n✨ Agent proposed a workflow plan: {plan.name}")
            decision, modification = self.plan_approval.request_approval(plan)

            if decision == "approve":
                # Execute the plan
                await self.execute_plan(plan)
            elif decision == "modify":
                print(f"\n📝 Please provide modified instructions to the agent:")
                print(f"   Agent will revise the plan based on: {modification}")
            else:
                print(f"\n❌ Plan rejected")
                del self.pending_plans[plan.plan_id]

        return plan

    async def execute_plan(self, plan: Plan):
        """Execute an approved workflow plan"""
        print(f"\n🚀 Executing workflow: {plan.name}\n")

        try:
            success, message = await self.workflow_engine.execute_plan(
                plan,
                auto_rollback=True,
                stop_on_error=True
            )

            # Display summary
            summary = self.workflow_engine.get_execution_summary()
            self.plan_approval.display_execution_summary(summary)

            if success:
                print(f"\n✅ Workflow completed successfully!")
            else:
                print(f"\n❌ Workflow failed: {message}")

            # Remove from pending
            if plan.plan_id in self.pending_plans:
                del self.pending_plans[plan.plan_id]

        except Exception as e:
            self.logger.error(f"Error executing plan: {e}", exc_info=True)
            print(f"\n❌ Error executing workflow: {e}")

    def list_pending_plans(self):
        """List all pending workflow plans"""
        if not self.pending_plans:
            print("\n📋 No pending workflow plans\n")
            return

        print("\n" + "=" * 70)
        print("📋 PENDING WORKFLOW PLANS")
        print("=" * 70)

        for plan_id, plan in self.pending_plans.items():
            print(f"\n🔹 {plan.name} [{plan_id}]")
            print(f"   Description: {plan.description}")
            print(f"   Steps: {len(plan.steps)}")
            print(f"   Estimated Time: {plan.get_total_estimated_time()}s")
            print(f"   Estimated Cost: ${plan.estimate_cost():.4f}")
            print(f"   Status: {'APPROVED' if plan.approved else 'PENDING APPROVAL'}")

        print("\n" + "=" * 70 + "\n")
        print("Use /approve <plan_id> to execute or /reject <plan_id> to discard\n")

    async def process_command(self, command: str) -> bool:
        """
        Process a system command

        Args:
            command: Command string (without leading /)

        Returns:
            True to continue, False to exit
        """
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == 'exit':
            return False

        elif cmd == 'help':
            self.print_help()

        elif cmd == 'spawn':
            if len(parts) < 2:
                print("❌ Usage: /spawn <role> <task_description>")
                print("   Example: /spawn reviewer Review the authentication code")
                return True

            args = parts[1].split(maxsplit=1)
            if len(args) < 2:
                print("❌ Please provide both role and task description")
                return True

            role = args[0]
            task = args[1]

            sub_agent = await self.spawn_sub_agent(role, task)

            if sub_agent:
                # Run the task
                task_coro = self.run_agent_task(sub_agent, task)
                task = asyncio.create_task(task_coro)
                self.running_tasks[sub_agent.agent_id] = task

        elif cmd == 'agents':
            self.list_agents()

        elif cmd == 'stats':
            self.show_stats()

        elif cmd == 'stop':
            if len(parts) < 2:
                print("❌ Usage: /stop <agent_id>")
                return True

            agent_id = parts[1].strip()
            self.agent_manager.terminate_agent(agent_id)
            print(f"✅ Agent {agent_id} terminated\n")

        elif cmd == 'stop_all':
            if self.main_agent:
                self.agent_manager.terminate_sub_agents(self.main_agent.agent_id)
                print("✅ All sub-agents terminated\n")

        elif cmd == 'config':
            if self.main_agent:
                print(f"\n{'='*70}")
                print("⚙️  CONFIGURATION")
                print(f"{'='*70}")
                print(f"Provider: {self.main_agent.config.provider}")
                print(f"URL: {self.main_agent.config.api_url}")
                print(f"Model: {self.main_agent.config.model_name}")
                print(f"Temperature: {self.main_agent.config.temperature}")
                print(f"Max tokens: {self.main_agent.config.max_tokens}")
                print(f"Streaming: {self.main_agent.config.stream}")
                print(f"Show thinking: {self.main_agent.config.show_thinking}")
                print(f"Show tokens: {self.main_agent.config.show_token_count}")
                print(f"{'='*70}\n")

        elif cmd == 'stream':
            if self.main_agent:
                self.main_agent.toggle_streaming()

        elif cmd == 'thinking':
            if self.main_agent:
                self.main_agent.toggle_thinking()

        elif cmd == 'reset':
            if self.main_agent:
                self.main_agent.reset_conversation()
                print("✅ Main agent conversation reset\n")

        elif cmd == 'auto_spawn':
            self.auto_spawn_enabled = not self.auto_spawn_enabled
            status = "enabled" if self.auto_spawn_enabled else "disabled"
            emoji = "✅" if self.auto_spawn_enabled else "❌"
            print(f"{emoji} Automatic sub-agent spawning {status}\n")

        # ===== PHASE 2: WORKFLOW COMMANDS =====

        elif cmd == 'plans':
            self.list_pending_plans()

        elif cmd == 'approve':
            if len(parts) < 2:
                print("❌ Usage: /approve <plan_id>")
                return True

            plan_id = parts[1].strip()
            if plan_id in self.pending_plans:
                plan = self.pending_plans[plan_id]
                plan.approved = True
                await self.execute_plan(plan)
            else:
                print(f"❌ Plan '{plan_id}' not found. Use /plans to list pending plans.\n")

        elif cmd == 'reject':
            if len(parts) < 2:
                print("❌ Usage: /reject <plan_id>")
                return True

            plan_id = parts[1].strip()
            if plan_id in self.pending_plans:
                plan = self.pending_plans[plan_id]
                print(f"❌ Plan '{plan.name}' [{plan_id}] rejected and removed\n")
                del self.pending_plans[plan_id]
            else:
                print(f"❌ Plan '{plan_id}' not found\n")

        elif cmd == 'plan':
            if len(parts) < 2:
                print("❌ Usage: /plan <plan_id>")
                return True

            plan_id = parts[1].strip()
            if plan_id in self.pending_plans:
                plan = self.pending_plans[plan_id]
                self.plan_approval.display_plan(plan)
            else:
                print(f"❌ Plan '{plan_id}' not found\n")

        elif cmd == 'cancel_workflow':
            self.workflow_engine.cancel()
            print("⚠️  Workflow cancellation requested\n")

        else:
            print(f"❌ Unknown command: /{cmd}")
            print("   Type /help for available commands\n")

        return True

    async def run(self):
        """Main event loop"""
        await self.initialize()

        self.print_help()

        print("Ready! Type your message or /help for commands.\n")

        try:
            while True:
                try:
                    # Get user input
                    user_input = await asyncio.to_thread(input, "\n💬 You: ")
                    user_input = user_input.strip()

                    if not user_input:
                        continue

                    # Handle commands
                    if user_input.startswith('/'):
                        should_continue = await self.process_command(user_input[1:])
                        if not should_continue:
                            break
                        continue

                    # Handle directed messages (@agent_id message)
                    if user_input.startswith('@'):
                        parts = user_input[1:].split(maxsplit=1)
                        if len(parts) < 2:
                            print("❌ Usage: @<agent_id> <message>")
                            continue

                        agent_id = parts[0]
                        message = parts[1]

                        agent = self.agent_manager.get_agent(agent_id)
                        if agent:
                            await self.run_agent_task(agent, message)
                        else:
                            print(f"❌ Agent '{agent_id}' not found")
                        continue

                    # Check for auto-spawning keywords
                    spawned_agents = await self.check_and_auto_spawn(user_input)

                    # Send to main agent (even if sub-agents were spawned for coordination)
                    if self.main_agent:
                        await self.run_agent_task(self.main_agent, user_input)

                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrupted. Type /exit to quit.\n")
                    continue

        finally:
            await self.cleanup()

    async def cleanup(self):
        """Cleanup resources"""
        print("\n🔄 Cleaning up...\n")

        # Cancel running tasks
        for task in self.running_tasks.values():
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)

        # Cleanup agents
        for agent in self.agent_manager.agents.values():
            if isinstance(agent, AsyncStreamingAgent):
                await agent.cleanup()

        print("✅ Cleanup complete\n")


async def main():
    """Main entry point"""
    orchestrator = MultiAgentOrchestrator(config_file="agent_config_multi_agent.json")
    await orchestrator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        logging.error("Fatal error", exc_info=True)
