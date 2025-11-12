"""
Output Manager - Handles multiplexed output from multiple agents
Provides visual separation and prevents output collision
"""

import threading
import sys
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OutputType(Enum):
    """Type of output message"""
    NORMAL = "normal"
    THINKING = "thinking"
    SUMMARY = "summary"
    STATUS = "status"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class OutputMessage:
    """A message to be displayed"""
    agent_id: str
    agent_role: str
    content: str
    output_type: OutputType = OutputType.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    is_complete: bool = False  # True when message is fully streamed


class OutputManager:
    """Manages output from multiple agents with visual separation"""

    # ANSI color codes
    COLORS = {
        "main": "\033[94m",      # Blue
        "reviewer": "\033[95m",   # Magenta
        "researcher": "\033[96m", # Cyan
        "implementer": "\033[92m",# Green
        "tester": "\033[93m",     # Yellow
        "optimizer": "\033[91m",  # Red
        "general": "\033[97m",    # White
        "dim": "\033[90m",        # Dim
        "reset": "\033[0m",       # Reset
        "bold": "\033[1m",        # Bold
        "success": "\033[92m",    # Green
        "error": "\033[91m",      # Red
        "warning": "\033[93m",    # Yellow
    }

    # Role emoji indicators
    ROLE_EMOJI = {
        "main": "🤖",
        "reviewer": "🔍",
        "researcher": "📚",
        "implementer": "⚙️",
        "tester": "🧪",
        "optimizer": "⚡",
        "general": "💡",
    }

    # Status emoji
    STATUS_EMOJI = {
        "idle": "⏸️",
        "working": "⚙️",
        "waiting": "⏳",
        "completed": "✅",
        "error": "❌",
        "terminated": "🛑",
    }

    def __init__(self, enable_colors: bool = True):
        """
        Initialize the output manager

        Args:
            enable_colors: Whether to use ANSI colors
        """
        self.enable_colors = enable_colors
        self.lock = threading.Lock()
        self.current_agent: Optional[str] = None  # Track which agent is currently outputting
        self.agent_buffers: Dict[str, List[str]] = {}  # Buffer incomplete lines per agent
        self.agent_roles: Dict[str, str] = {}  # Track agent roles

        # Statistics
        self.message_counts: Dict[str, int] = {}

    def register_agent(self, agent_id: str, role: str):
        """
        Register an agent with the output manager

        Args:
            agent_id: Unique agent identifier
            role: Agent role (main, reviewer, etc.)
        """
        with self.lock:
            self.agent_buffers[agent_id] = []
            self.agent_roles[agent_id] = role
            self.message_counts[agent_id] = 0

    def _get_color(self, key: str) -> str:
        """Get ANSI color code if colors are enabled"""
        if self.enable_colors:
            return self.COLORS.get(key, "")
        return ""

    def _get_role_emoji(self, role: str) -> str:
        """Get emoji for role"""
        return self.ROLE_EMOJI.get(role, "🤖")

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        return self.STATUS_EMOJI.get(status, "")

    def print_agent_header(self, agent_id: str, role: str, status: str = "working"):
        """
        Print a header for agent output

        Args:
            agent_id: Agent identifier
            role: Agent role
            status: Current status
        """
        with self.lock:
            emoji = self._get_role_emoji(role)
            status_emoji = self._get_status_emoji(status)
            color = self._get_color(role)
            bold = self._get_color("bold")
            reset = self._get_color("reset")

            header = (
                f"\n{color}{bold}{'='*60}{reset}\n"
                f"{color}{bold}{emoji} Agent [{role.upper()}] {status_emoji} {status.upper()}{reset}\n"
                f"{color}ID: {agent_id}{reset}\n"
                f"{color}{bold}{'='*60}{reset}\n"
            )

            sys.stdout.write(header)
            sys.stdout.flush()

    def print_separator(self, agent_id: str, role: str):
        """Print a visual separator between agents"""
        with self.lock:
            color = self._get_color(role)
            reset = self._get_color("reset")
            separator = f"{color}{'-'*60}{reset}\n"

            sys.stdout.write(separator)
            sys.stdout.flush()

    def write(
        self,
        agent_id: str,
        content: str,
        output_type: OutputType = OutputType.NORMAL,
        flush: bool = True
    ):
        """
        Write output from an agent

        Args:
            agent_id: Agent identifier
            content: Content to write
            output_type: Type of output
            flush: Whether to flush immediately
        """
        with self.lock:
            role = self.agent_roles.get(agent_id, "general")

            # Switch agent context if needed
            if self.current_agent != agent_id:
                if self.current_agent is not None:
                    # Print separator when switching agents
                    old_role = self.agent_roles.get(self.current_agent, "general")
                    self.print_separator(self.current_agent, old_role)

                self.current_agent = agent_id
                self.message_counts[agent_id] = self.message_counts.get(agent_id, 0) + 1

            # Apply formatting based on output type
            formatted_content = self._format_content(content, output_type, role)

            sys.stdout.write(formatted_content)
            if flush:
                sys.stdout.flush()

    def _format_content(self, content: str, output_type: OutputType, role: str) -> str:
        """
        Format content based on output type

        Args:
            content: Raw content
            output_type: Type of output
            role: Agent role

        Returns:
            Formatted content with ANSI codes
        """
        if not self.enable_colors:
            return content

        reset = self.COLORS["reset"]

        if output_type == OutputType.THINKING:
            # Dim gray for thinking
            return f"{self.COLORS['dim']}{content}{reset}"

        elif output_type == OutputType.SUMMARY:
            # Bold with agent color for summaries
            color = self.COLORS.get(role, "")
            return f"{self.COLORS['bold']}{color}📋 SUMMARY: {content}{reset}"

        elif output_type == OutputType.ERROR:
            # Red for errors
            return f"{self.COLORS['error']}❌ {content}{reset}"

        elif output_type == OutputType.SUCCESS:
            # Green for success
            return f"{self.COLORS['success']}✅ {content}{reset}"

        elif output_type == OutputType.STATUS:
            # Yellow for status updates
            return f"{self.COLORS['warning']}ℹ️  {content}{reset}"

        else:  # NORMAL
            # Agent role color
            color = self.COLORS.get(role, "")
            return f"{color}{content}{reset}"

    def write_summary(self, agent_id: str, summary: str):
        """
        Write a summary from a sub-agent

        Args:
            agent_id: Agent identifier
            summary: Summary content
        """
        with self.lock:
            role = self.agent_roles.get(agent_id, "general")
            emoji = self._get_role_emoji(role)
            color = self._get_color(role)
            bold = self._get_color("bold")
            reset = self._get_color("reset")

            formatted = (
                f"\n{color}{bold}{'='*60}{reset}\n"
                f"{color}{bold}{emoji} SUMMARY FROM {role.upper()} AGENT{reset}\n"
                f"{color}ID: {agent_id}{reset}\n"
                f"{color}{bold}{'='*60}{reset}\n"
                f"{summary}\n"
                f"{color}{bold}{'='*60}{reset}\n"
            )

            sys.stdout.write(formatted)
            sys.stdout.flush()

    def write_status(self, agent_id: str, status: str, message: str = ""):
        """
        Write a status update for an agent

        Args:
            agent_id: Agent identifier
            status: Status (idle, working, completed, etc.)
            message: Optional message to accompany status
        """
        with self.lock:
            role = self.agent_roles.get(agent_id, "general")
            emoji = self._get_role_emoji(role)
            status_emoji = self._get_status_emoji(status)
            color = self._get_color(role)
            reset = self._get_color("reset")

            status_text = f"{color}{emoji} Agent [{agent_id}] {status_emoji} {status.upper()}{reset}"
            if message:
                status_text += f" - {message}"

            sys.stdout.write(f"\n{status_text}\n")
            sys.stdout.flush()

    def write_error(self, agent_id: str, error: str):
        """
        Write an error message

        Args:
            agent_id: Agent identifier
            error: Error message
        """
        self.write(agent_id, f"\n❌ ERROR: {error}\n", OutputType.ERROR)

    def write_success(self, agent_id: str, message: str):
        """
        Write a success message

        Args:
            agent_id: Agent identifier
            message: Success message
        """
        self.write(agent_id, f"\n✅ {message}\n", OutputType.SUCCESS)

    def finalize_agent_output(self, agent_id: str):
        """
        Finalize output from an agent (called when agent completes)

        Args:
            agent_id: Agent identifier
        """
        with self.lock:
            role = self.agent_roles.get(agent_id, "general")
            self.print_separator(agent_id, role)

            if self.current_agent == agent_id:
                self.current_agent = None

    def get_statistics(self) -> Dict[str, int]:
        """Get output statistics"""
        with self.lock:
            return self.message_counts.copy()

    def clear(self):
        """Clear all output buffers"""
        with self.lock:
            self.agent_buffers.clear()
            self.message_counts.clear()
            self.current_agent = None
