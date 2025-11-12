"""
Async Streaming Agent - Extends StreamingAgent with async/await support
Enables concurrent execution of multiple agents
"""

import asyncio
import aiohttp
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass

from coding_agent_streaming import AgentConfig, StreamingAgent
from agent_manager import AgentManager, AgentRole, AgentStatus
from output_manager import OutputManager, OutputType
from tool_executor import ToolExecutor, ExecutionResult


class AsyncStreamingAgent(StreamingAgent):
    """
    Async version of StreamingAgent with concurrent execution support
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        agent_manager: Optional[AgentManager] = None,
        output_manager: Optional[OutputManager] = None,
        agent_id: Optional[str] = None,
        role: Optional[AgentRole] = None,
        tool_executor: Optional[ToolExecutor] = None
    ):
        """
        Initialize async streaming agent

        Args:
            config: Agent configuration
            agent_manager: Agent manager instance
            output_manager: Output manager instance
            agent_id: Unique agent ID (assigned by manager)
            role: Agent role
            tool_executor: Tool executor for running commands and file operations
        """
        super().__init__(config)

        self.agent_manager = agent_manager
        self.output_manager = output_manager
        self.agent_id = agent_id or "main"
        self.role = role or AgentRole.MAIN
        self.tool_executor = tool_executor

        # File operation lock for concurrent safety
        self._file_lock = threading.RLock()

        # Session for aiohttp (reusable connection pool)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=120)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def _close_session(self):
        """Close aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _stream_response_async(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from API using async/await

        Args:
            messages: Conversation history

        Yields:
            Token strings
        """
        self.response_start_time = time.time()
        self.token_count = 0

        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        endpoint = self._get_api_endpoint()
        request_payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True
        }

        self.logger.info(f"[{self.agent_id}] Making async streaming request to: {endpoint}")
        self.logger.debug(f"[{self.agent_id}] Request payload: {json.dumps(request_payload, indent=2)}")

        session = await self._get_session()

        try:
            async with session.post(
                endpoint,
                json=request_payload,
                headers=headers
            ) as response:
                self.logger.info(f"[{self.agent_id}] Response status: {response.status}")
                response.raise_for_status()

                async for line in response.content:
                    if line:
                        line_str = line.decode('utf-8').strip()

                        if line_str.startswith('data: '):
                            data_str = line_str[6:]

                            if data_str == '[DONE]':
                                self.logger.debug(f"[{self.agent_id}] Received [DONE]")
                                break

                            try:
                                data = json.loads(data_str)

                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        self.token_count += 1
                                        yield content
                            except json.JSONDecodeError:
                                continue

            self.logger.info(
                f"[{self.agent_id}] Streaming complete. "
                f"Total tokens: {self.token_count}"
            )

        except aiohttp.ClientError as e:
            self.logger.error(f"[{self.agent_id}] Connection error: {e}")
            raise ConnectionError(
                f"Cannot connect to {self.config.provider} at {self.config.api_url}. "
                f"Error: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"[{self.agent_id}] Streaming error: {e}", exc_info=True)
            raise Exception(f"Streaming failed: {str(e)}")

    async def process_message_async(
        self,
        user_message: str,
        use_output_manager: bool = True
    ) -> str:
        """
        Process message asynchronously

        Args:
            user_message: User input
            use_output_manager: Whether to use output manager for display

        Returns:
            Assistant response
        """
        # Update agent status
        if self.agent_manager:
            self.agent_manager.update_status(self.agent_id, AgentStatus.WORKING)

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Write to output
        if use_output_manager and self.output_manager:
            self.output_manager.write(
                self.agent_id,
                f"\nProcessing: {user_message[:100]}...\n",
                OutputType.STATUS
            )

        full_response = ""
        in_thinking = False
        thinking_content = ""
        in_summary = False
        summary_content = ""

        try:
            async for token in self._stream_response_async(self.conversation_history):
                full_response += token

                # Parse special tags
                if self.config.show_thinking:
                    # Handle [THINKING] tags
                    if '[THINKING]' in full_response and not in_thinking:
                        in_thinking = True
                        thinking_start = full_response.index('[THINKING]')
                        pre_thinking = full_response[:thinking_start]

                        if pre_thinking and use_output_manager and self.output_manager:
                            self.output_manager.write(
                                self.agent_id,
                                pre_thinking,
                                OutputType.NORMAL
                            )

                        full_response = full_response[thinking_start + len('[THINKING]'):]
                        thinking_content = ""

                    elif '[/THINKING]' in full_response and in_thinking:
                        in_thinking = False
                        thinking_end = full_response.index('[/THINKING]')
                        thinking_content += full_response[:thinking_end]

                        if use_output_manager and self.output_manager:
                            self.output_manager.write(
                                self.agent_id,
                                thinking_content,
                                OutputType.THINKING
                            )

                        full_response = full_response[thinking_end + len('[/THINKING]'):]

                        # Skip [RESPONSE] tag if present
                        if '[RESPONSE]' in full_response:
                            full_response = full_response[
                                full_response.index('[RESPONSE]') + len('[RESPONSE]'):
                            ]

                    elif in_thinking:
                        thinking_content += token
                        continue

                # Handle [SUMMARY] tags for sub-agents
                if '[SUMMARY]' in full_response and not in_summary:
                    in_summary = True
                    summary_start = full_response.index('[SUMMARY]')
                    pre_summary = full_response[:summary_start]

                    if pre_summary and use_output_manager and self.output_manager:
                        self.output_manager.write(
                            self.agent_id,
                            pre_summary,
                            OutputType.NORMAL
                        )

                    full_response = full_response[summary_start + len('[SUMMARY]'):]
                    summary_content = ""

                elif '[/SUMMARY]' in full_response and in_summary:
                    in_summary = False
                    summary_end = full_response.index('[/SUMMARY]')
                    summary_content += full_response[:summary_end]

                    # Send summary to agent manager
                    if self.agent_manager:
                        self.agent_manager.add_summary(self.agent_id, summary_content)

                    # Display summary
                    if use_output_manager and self.output_manager:
                        self.output_manager.write_summary(
                            self.agent_id,
                            summary_content
                        )

                    full_response = full_response[summary_end + len('[/SUMMARY]'):]

                elif in_summary:
                    summary_content += token
                    continue

                # Regular output
                if not in_thinking and not in_summary:
                    if use_output_manager and self.output_manager:
                        self.output_manager.write(
                            self.agent_id,
                            token,
                            OutputType.NORMAL
                        )

            # Final newline
            if use_output_manager and self.output_manager:
                self.output_manager.write(self.agent_id, "\n", OutputType.NORMAL)

            # Show statistics
            if self.config.show_token_count and self.response_start_time:
                elapsed = time.time() - self.response_start_time
                tokens_per_second = self.token_count / elapsed if elapsed > 0 else 0

                stats_msg = (
                    f"\n[{self.token_count} tokens | "
                    f"{elapsed:.1f}s | "
                    f"{tokens_per_second:.1f} tok/s]\n"
                )

                if use_output_manager and self.output_manager:
                    self.output_manager.write(
                        self.agent_id,
                        stats_msg,
                        OutputType.STATUS
                    )

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })

            # Update status
            if self.agent_manager:
                self.agent_manager.update_status(self.agent_id, AgentStatus.COMPLETED)

            return full_response

        except Exception as e:
            # Remove user message on error
            self.conversation_history.pop()

            if use_output_manager and self.output_manager:
                self.output_manager.write_error(self.agent_id, str(e))

            if self.agent_manager:
                self.agent_manager.update_status(self.agent_id, AgentStatus.ERROR)

            raise e

    def write_file_locked(self, file_path: str, content: str) -> tuple[bool, str]:
        """Thread-safe file write"""
        with self._file_lock:
            return self.write_file(file_path, content)

    def edit_file_locked(
        self,
        file_path: str,
        find_text: str,
        replace_text: str
    ) -> tuple[bool, str]:
        """Thread-safe file edit"""
        with self._file_lock:
            return self.edit_file(file_path, find_text, replace_text)

    def read_file_locked(self, file_path: str) -> tuple[bool, str]:
        """Thread-safe file read"""
        with self._file_lock:
            return self.read_file(file_path)

    async def cleanup(self):
        """Cleanup resources"""
        await self._close_session()
        self.logger.info(f"[{self.agent_id}] Cleanup complete")

    # Tool execution methods
    async def execute_bash(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute a bash command safely

        Args:
            command: Bash command to execute
            working_dir: Optional working directory
            timeout: Optional timeout in seconds

        Returns:
            ExecutionResult with command output
        """
        if not self.tool_executor:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message="ToolExecutor not initialized for this agent"
            )

        wd = Path(working_dir) if working_dir else None
        return await self.tool_executor.execute_bash(command, wd, timeout)

    async def execute_python_script(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute a Python script

        Args:
            script_path: Path to Python script
            args: Optional command line arguments
            timeout: Optional timeout in seconds

        Returns:
            ExecutionResult with script output
        """
        if not self.tool_executor:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message="ToolExecutor not initialized for this agent"
            )

        return await self.tool_executor.execute_python_script(Path(script_path), args, timeout)

    async def read_file_tool(self, file_path: str) -> ExecutionResult:
        """
        Read a file using ToolExecutor

        Args:
            file_path: Path to file

        Returns:
            ExecutionResult with file contents
        """
        if not self.tool_executor:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message="ToolExecutor not initialized for this agent"
            )

        return await self.tool_executor.read_file(Path(file_path))

    async def write_file_tool(
        self,
        file_path: str,
        content: str,
        overwrite: bool = False
    ) -> ExecutionResult:
        """
        Write to a file using ToolExecutor

        Args:
            file_path: Path to file
            content: Content to write
            overwrite: Whether to overwrite existing file

        Returns:
            ExecutionResult indicating success
        """
        if not self.tool_executor:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message="ToolExecutor not initialized for this agent"
            )

        return await self.tool_executor.write_file(Path(file_path), content, overwrite)

    async def list_files_tool(
        self,
        directory: str,
        pattern: str = "*"
    ) -> ExecutionResult:
        """
        List files in a directory

        Args:
            directory: Directory to list
            pattern: Glob pattern

        Returns:
            ExecutionResult with file list (JSON)
        """
        if not self.tool_executor:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message="ToolExecutor not initialized for this agent"
            )

        return await self.tool_executor.list_files(Path(directory), pattern)


@dataclass
class MultiAgentConfig:
    """Configuration for multi-agent system"""
    config_file: str = "agent_config_multi_agent.json"
    main_profile: str = "main_agent"
    enable_auto_spawning: bool = True
    max_concurrent_agents: int = 4
    secrets_file: str = "secrets.json"


def load_multi_agent_config(config_file: str = "agent_config_multi_agent.json") -> Dict[str, Any]:
    """
    Load multi-agent configuration from file

    Args:
        config_file: Path to configuration file

    Returns:
        Configuration dictionary
    """
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Load API keys from secrets if needed
    secrets_path = Path("secrets.json")
    if secrets_path.exists():
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)

        # Update API keys in profiles
        for profile_name, profile in config.get("agent_profiles", {}).items():
            if profile.get("api_key") == "YOUR_API_KEY_HERE":
                provider = profile.get("provider", "")
                if provider == "ollama":
                    profile["api_key"] = secrets.get("ollama_api_key")
                elif provider == "lm_studio":
                    profile["api_key"] = secrets.get("lm_studio_api_key")

    return config


def create_agent_from_profile(
    profile_name: str,
    config_dict: Dict[str, Any],
    agent_manager: AgentManager,
    output_manager: OutputManager,
    tool_executor: Optional[ToolExecutor] = None,
    parent_id: Optional[str] = None,
    task_description: Optional[str] = None
) -> AsyncStreamingAgent:
    """
    Create an agent from a profile in the config

    Args:
        profile_name: Name of the profile to use
        config_dict: Full configuration dictionary
        agent_manager: Agent manager instance
        output_manager: Output manager instance
        tool_executor: Tool executor for running commands and file operations
        parent_id: Parent agent ID (for sub-agents)
        task_description: Description of agent's task

    Returns:
        Configured AsyncStreamingAgent instance
    """
    profiles = config_dict.get("agent_profiles", {})

    if profile_name not in profiles:
        raise ValueError(f"Profile '{profile_name}' not found in configuration")

    profile = profiles[profile_name]

    # Load system prompt
    prompt_file = profile.get("system_prompt_file", "system_prompt.txt")
    prompt_path = Path(prompt_file)

    if prompt_path.exists():
        with open(prompt_path, 'r') as f:
            system_prompt = f.read()
    else:
        system_prompt = "You are a helpful AI assistant."

    # Create AgentConfig
    agent_config = AgentConfig(
        provider=profile.get("provider", "ollama"),
        api_url=profile.get("url", "http://localhost:1234/v1"),
        model_name=profile.get("model", "gpt-oss:120b-cloud"),
        api_key=profile.get("api_key"),
        temperature=profile.get("temperature", 0.7),
        max_tokens=profile.get("max_tokens", 4096),
        stream=profile.get("stream", True),
        show_token_count=profile.get("show_token_count", True),
        show_thinking=profile.get("show_thinking", True)
    )

    # Map role string to AgentRole enum
    role_mapping = {
        "main": AgentRole.MAIN,
        "reviewer": AgentRole.REVIEWER,
        "researcher": AgentRole.RESEARCHER,
        "implementer": AgentRole.IMPLEMENTER,
        "tester": AgentRole.TESTER,
        "optimizer": AgentRole.OPTIMIZER,
        "general": AgentRole.GENERAL
    }

    role_str = profile.get("role", "general")
    role = role_mapping.get(role_str, AgentRole.GENERAL)

    # Create agent instance
    agent = AsyncStreamingAgent(
        config=agent_config,
        agent_manager=agent_manager,
        output_manager=output_manager,
        tool_executor=tool_executor,
        role=role
    )

    # Override system prompt
    agent.system_prompt = system_prompt
    agent.conversation_history = [{"role": "system", "content": system_prompt}]

    # Register with manager
    is_main = (role == AgentRole.MAIN and parent_id is None)
    agent_id = agent_manager.register_agent(
        agent=agent,
        role=role,
        parent_id=parent_id,
        task_description=task_description,
        is_main=is_main
    )

    agent.agent_id = agent_id

    # Register with output manager
    output_manager.register_agent(agent_id, role_str)

    return agent
