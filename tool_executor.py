"""
Tool Executor
Provides safe execution of bash commands, Python scripts, and file operations for agents
"""

import asyncio
import subprocess
import os
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass
import logging


@dataclass
class ExecutionResult:
    """Result of a tool execution"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    error_message: Optional[str] = None
    execution_time: float = 0.0


class ToolExecutor:
    """Executes tools safely for AI agents"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the tool executor

        Args:
            config: Configuration dictionary with agent_settings and file_operations
        """
        self.config = config
        self.logger = logging.getLogger('ToolExecutor')

        # Extract settings
        agent_settings = config.get("agent_settings", {})
        file_ops = config.get("file_operations", {})

        self.safe_mode = agent_settings.get("safe_mode", True)
        self.timeout_seconds = agent_settings.get("timeout_seconds", 60)
        self.code_execution_timeout = agent_settings.get("timeout_overrides", {}).get("code_execution", 180)

        self.allow_file_write = file_ops.get("allow_file_write", True)
        self.allow_file_read = file_ops.get("allow_file_read", True)
        self.allowed_directories = [Path(d) for d in file_ops.get("allowed_directories", [])]
        self.max_file_size_kb = file_ops.get("max_file_size_kb", 500)

        # Whitelist of safe bash commands
        self.safe_bash_commands = {
            'ls', 'cat', 'pwd', 'echo', 'grep', 'find', 'wc', 'head', 'tail',
            'mkdir', 'touch', 'cp', 'mv', 'python', 'python3', 'pip', 'git',
            'node', 'npm', 'pytest', 'test', 'diff', 'sort', 'uniq', 'sed', 'awk'
        }

        # Blacklist of dangerous commands
        self.dangerous_commands = {
            'rm', 'rmdir', 'dd', 'mkfs', 'format', 'fdisk', 'chmod', 'chown',
            'sudo', 'su', 'kill', 'killall', 'reboot', 'shutdown', 'halt',
            'systemctl', 'service'
        }

    def _is_path_allowed(self, path: Path) -> bool:
        """Check if a path is within allowed directories"""
        if not self.allowed_directories:
            return True

        try:
            path = path.resolve()
            for allowed_dir in self.allowed_directories:
                allowed_dir = allowed_dir.resolve()
                if path == allowed_dir or allowed_dir in path.parents:
                    return True
        except Exception as e:
            self.logger.error(f"Error checking path {path}: {e}")
            return False

        return False

    def _validate_bash_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a bash command for safety

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command or not command.strip():
            return False, "Empty command"

        # Extract the base command
        base_command = command.strip().split()[0]

        # Remove leading path if present
        base_command = os.path.basename(base_command)

        # Check for dangerous commands
        if base_command in self.dangerous_commands:
            return False, f"Dangerous command '{base_command}' not allowed in safe mode"

        # In safe mode, only allow whitelisted commands
        if self.safe_mode and base_command not in self.safe_bash_commands:
            return False, f"Command '{base_command}' not in safe command whitelist"

        # Check for command chaining that might be dangerous
        dangerous_patterns = [';', '&&', '||', '|', '>', '>>', '<']
        if self.safe_mode:
            for pattern in dangerous_patterns:
                if pattern in command:
                    # Allow some safe patterns like pipes to grep
                    if pattern == '|' and any(safe in command for safe in ['grep', 'wc', 'sort', 'head', 'tail']):
                        continue
                    return False, f"Command chaining pattern '{pattern}' not allowed in safe mode"

        return True, None

    async def execute_bash(
        self,
        command: str,
        working_dir: Optional[Path] = None,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute a bash command safely

        Args:
            command: Command to execute
            working_dir: Optional working directory
            timeout: Optional timeout override

        Returns:
            ExecutionResult with command output
        """
        # Validate command
        is_valid, error = self._validate_bash_command(command)
        if not is_valid:
            self.logger.warning(f"Blocked unsafe command: {command}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Command blocked: {error}"
            )

        # Check working directory
        if working_dir and not self._is_path_allowed(working_dir):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Working directory {working_dir} not in allowed directories"
            )

        # Execute command
        timeout_val = timeout or self.timeout_seconds

        try:
            import time
            start_time = time.time()

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_val
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode('utf-8', errors='replace'),
                stderr=stderr.decode('utf-8', errors='replace'),
                return_code=process.returncode,
                execution_time=execution_time
            )

        except asyncio.TimeoutError:
            self.logger.error(f"Command timeout: {command}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Command timed out after {timeout_val} seconds"
            )
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=str(e)
            )

    async def execute_python_script(
        self,
        script_path: Path,
        args: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute a Python script

        Args:
            script_path: Path to Python script
            args: Optional command line arguments
            timeout: Optional timeout override

        Returns:
            ExecutionResult with script output
        """
        # Check if file exists and is allowed
        if not script_path.exists():
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Script not found: {script_path}"
            )

        if not self._is_path_allowed(script_path):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Script {script_path} not in allowed directories"
            )

        # Build command
        cmd_parts = ["python3", str(script_path)]
        if args:
            cmd_parts.extend(args)
        command = " ".join(cmd_parts)

        # Execute using bash executor with code execution timeout
        return await self.execute_bash(
            command,
            timeout=timeout or self.code_execution_timeout
        )

    async def read_file(self, file_path: Path) -> ExecutionResult:
        """
        Read a file safely

        Args:
            file_path: Path to file

        Returns:
            ExecutionResult with file contents in stdout
        """
        if not self.allow_file_read:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message="File read operations are disabled"
            )

        if not self._is_path_allowed(file_path):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"File {file_path} not in allowed directories"
            )

        try:
            # Check file size
            size_kb = file_path.stat().st_size / 1024
            if size_kb > self.max_file_size_kb:
                return ExecutionResult(
                    success=False,
                    stdout="",
                    stderr="",
                    return_code=-1,
                    error_message=f"File too large: {size_kb:.1f}KB (max: {self.max_file_size_kb}KB)"
                )

            content = file_path.read_text(encoding='utf-8')

            return ExecutionResult(
                success=True,
                stdout=content,
                stderr="",
                return_code=0
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Error reading file: {e}"
            )

    async def write_file(
        self,
        file_path: Path,
        content: str,
        overwrite: bool = False
    ) -> ExecutionResult:
        """
        Write to a file safely

        Args:
            file_path: Path to file
            content: Content to write
            overwrite: Whether to overwrite existing file

        Returns:
            ExecutionResult indicating success
        """
        if not self.allow_file_write:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message="File write operations are disabled"
            )

        if not self._is_path_allowed(file_path):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"File {file_path} not in allowed directories"
            )

        # Check if file exists and overwrite is not allowed
        if file_path.exists() and not overwrite:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"File {file_path} already exists (use overwrite=True to replace)"
            )

        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_text(content, encoding='utf-8')

            return ExecutionResult(
                success=True,
                stdout=f"Written {len(content)} bytes to {file_path}",
                stderr="",
                return_code=0
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Error writing file: {e}"
            )

    async def list_files(
        self,
        directory: Path,
        pattern: str = "*"
    ) -> ExecutionResult:
        """
        List files in a directory

        Args:
            directory: Directory to list
            pattern: Glob pattern (default: *)

        Returns:
            ExecutionResult with file list in stdout (JSON)
        """
        if not self._is_path_allowed(directory):
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Directory {directory} not in allowed directories"
            )

        try:
            files = list(directory.glob(pattern))
            file_info = [
                {
                    "name": f.name,
                    "path": str(f),
                    "is_file": f.is_file(),
                    "is_dir": f.is_dir(),
                    "size": f.stat().st_size if f.is_file() else 0
                }
                for f in files
            ]

            return ExecutionResult(
                success=True,
                stdout=json.dumps(file_info, indent=2),
                stderr="",
                return_code=0
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                error_message=f"Error listing files: {e}"
            )
