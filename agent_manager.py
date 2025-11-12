"""
Agent Manager - Orchestrates multiple AI agents
Handles lifecycle, communication, and coordination between main and sub-agents
"""

import asyncio
import threading
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging


class AgentStatus(Enum):
    """Status of an agent"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"
    TERMINATED = "terminated"


class AgentRole(Enum):
    """Role of an agent in the system"""
    MAIN = "main"
    REVIEWER = "reviewer"
    RESEARCHER = "researcher"
    IMPLEMENTER = "implementer"
    TESTER = "tester"
    OPTIMIZER = "optimizer"
    GENERAL = "general"


@dataclass
class AgentInfo:
    """Information about a managed agent"""
    agent_id: str
    role: AgentRole
    model_name: str
    provider: str
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None  # For sub-agents
    task_description: Optional[str] = None
    is_main: bool = False
    summaries: List[str] = field(default_factory=list)  # Summaries sent to main agent

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "model_name": self.model_name,
            "provider": self.provider,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "parent_id": self.parent_id,
            "task_description": self.task_description,
            "is_main": self.is_main
        }


class AgentManager:
    """Manages multiple agent instances and their coordination"""

    def __init__(self, output_callback: Optional[Callable] = None):
        """
        Initialize the agent manager

        Args:
            output_callback: Function to call when an agent produces output
                           Signature: callback(agent_id, message, is_summary)
        """
        self.agents: Dict[str, 'StreamingAgent'] = {}
        self.agent_info: Dict[str, AgentInfo] = {}
        self.main_agent_id: Optional[str] = None
        self.output_callback = output_callback
        self.lock = threading.RLock()  # Reentrant lock for thread safety

        # Set up logging
        self.logger = logging.getLogger('AgentManager')
        self.logger.setLevel(logging.DEBUG)

        # Communication queues for inter-agent messages
        self.message_queues: Dict[str, asyncio.Queue] = {}

        self.logger.info("AgentManager initialized")

    def register_agent(
        self,
        agent: 'StreamingAgent',
        role: AgentRole,
        parent_id: Optional[str] = None,
        task_description: Optional[str] = None,
        is_main: bool = False
    ) -> str:
        """
        Register a new agent with the manager

        Args:
            agent: The StreamingAgent instance
            role: Role of the agent
            parent_id: ID of parent agent (for sub-agents)
            task_description: Description of the agent's task
            is_main: Whether this is the main agent

        Returns:
            agent_id: Unique identifier for the agent
        """
        with self.lock:
            agent_id = str(uuid.uuid4())[:8]  # Short UUID

            info = AgentInfo(
                agent_id=agent_id,
                role=role,
                model_name=agent.config.model_name,
                provider=agent.config.provider,
                parent_id=parent_id,
                task_description=task_description,
                is_main=is_main
            )

            self.agents[agent_id] = agent
            self.agent_info[agent_id] = info

            # Set up message queue for this agent
            self.message_queues[agent_id] = asyncio.Queue()

            if is_main:
                self.main_agent_id = agent_id

            self.logger.info(
                f"Registered agent {agent_id} "
                f"(role={role.value}, model={agent.config.model_name}, "
                f"is_main={is_main})"
            )

            return agent_id

    def get_agent(self, agent_id: str) -> Optional['StreamingAgent']:
        """Get agent instance by ID"""
        return self.agents.get(agent_id)

    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent info by ID"""
        return self.agent_info.get(agent_id)

    def get_main_agent(self) -> Optional['StreamingAgent']:
        """Get the main agent"""
        if self.main_agent_id:
            return self.agents.get(self.main_agent_id)
        return None

    def list_agents(self, include_terminated: bool = False) -> List[AgentInfo]:
        """
        List all agents

        Args:
            include_terminated: Include terminated agents

        Returns:
            List of agent info objects
        """
        with self.lock:
            if include_terminated:
                return list(self.agent_info.values())
            else:
                return [
                    info for info in self.agent_info.values()
                    if info.status != AgentStatus.TERMINATED
                ]

    def get_sub_agents(self, parent_id: str) -> List[AgentInfo]:
        """Get all sub-agents of a specific parent"""
        with self.lock:
            return [
                info for info in self.agent_info.values()
                if info.parent_id == parent_id
            ]

    def update_status(self, agent_id: str, status: AgentStatus):
        """Update agent status"""
        with self.lock:
            if agent_id in self.agent_info:
                self.agent_info[agent_id].status = status
                self.logger.debug(f"Agent {agent_id} status updated to {status.value}")

    def add_summary(self, agent_id: str, summary: str):
        """
        Add a summary from a sub-agent

        This summary will be forwarded to the main agent

        Args:
            agent_id: ID of the agent producing the summary
            summary: Summary text to forward
        """
        with self.lock:
            if agent_id in self.agent_info:
                self.agent_info[agent_id].summaries.append(summary)
                self.logger.info(f"Summary added from agent {agent_id}: {summary[:100]}...")

                # If there's an output callback, notify
                if self.output_callback:
                    self.output_callback(agent_id, summary, is_summary=True)

    def get_summaries(self, agent_id: str) -> List[str]:
        """Get all summaries from an agent"""
        with self.lock:
            if agent_id in self.agent_info:
                return self.agent_info[agent_id].summaries.copy()
            return []

    async def send_message(self, from_agent_id: str, to_agent_id: str, message: str):
        """
        Send a message from one agent to another

        Args:
            from_agent_id: Source agent ID
            to_agent_id: Destination agent ID
            message: Message content
        """
        if to_agent_id in self.message_queues:
            await self.message_queues[to_agent_id].put({
                "from": from_agent_id,
                "message": message,
                "timestamp": datetime.now()
            })
            self.logger.debug(f"Message queued: {from_agent_id} -> {to_agent_id}")

    async def receive_messages(self, agent_id: str, timeout: float = 0.1) -> List[Dict]:
        """
        Receive pending messages for an agent

        Args:
            agent_id: Agent ID to check for messages
            timeout: Timeout in seconds for checking

        Returns:
            List of messages
        """
        messages = []
        if agent_id not in self.message_queues:
            return messages

        queue = self.message_queues[agent_id]
        try:
            while True:
                msg = await asyncio.wait_for(queue.get(), timeout=timeout)
                messages.append(msg)
        except asyncio.TimeoutError:
            pass  # No more messages

        return messages

    def terminate_agent(self, agent_id: str):
        """
        Terminate an agent

        Args:
            agent_id: ID of agent to terminate
        """
        with self.lock:
            if agent_id in self.agent_info:
                self.update_status(agent_id, AgentStatus.TERMINATED)
                self.logger.info(f"Agent {agent_id} terminated")

                # Note: We keep the agent in memory for history access
                # Could optionally clean up here if needed

    def terminate_sub_agents(self, parent_id: str):
        """Terminate all sub-agents of a parent"""
        sub_agents = self.get_sub_agents(parent_id)
        for info in sub_agents:
            self.terminate_agent(info.agent_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about managed agents"""
        with self.lock:
            total = len(self.agent_info)
            active = sum(
                1 for info in self.agent_info.values()
                if info.status not in [AgentStatus.TERMINATED, AgentStatus.COMPLETED]
            )
            by_role = {}
            for info in self.agent_info.values():
                role = info.role.value
                by_role[role] = by_role.get(role, 0) + 1

            return {
                "total_agents": total,
                "active_agents": active,
                "main_agent_id": self.main_agent_id,
                "agents_by_role": by_role,
                "agents": [info.to_dict() for info in self.agent_info.values()]
            }

    def clear(self):
        """Clear all agents (for testing/reset)"""
        with self.lock:
            self.agents.clear()
            self.agent_info.clear()
            self.message_queues.clear()
            self.main_agent_id = None
            self.logger.info("AgentManager cleared")
