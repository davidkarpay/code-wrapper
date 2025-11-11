"""
Qwen2.5-Coder Agent via LM Studio - Streaming Version
Features real-time token generation display and thought visualization
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Generator
from datetime import datetime
import requests
from dataclasses import dataclass, asdict
import re
import sys
import time


@dataclass
class AgentConfig:
    """Configuration for the coding agent"""
    lm_studio_url: str = "http://localhost:1234/v1"
    model_name: str = "qwen2.5-coder-1.5b-instruct"
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = True  # Enable streaming by default
    show_token_count: bool = True  # Show token statistics
    show_thinking: bool = True  # Show model "thinking" process
    thinking_prefix: str = "[THINKING]"  # Prefix for thinking output
    workspace_dir: str = "./agent_workspace"
    enable_code_execution: bool = True
    safe_mode: bool = True
    # File operation settings
    plan_mode: bool = True  # Require approval before file operations
    allow_file_write: bool = True
    allow_file_edit: bool = True
    allow_file_read: bool = True
    allowed_directories: List[str] = None
    max_file_size_kb: int = 500
    backup_before_edit: bool = True
    overwrite_warning: bool = True


class StreamingAgent:
    """Streaming coding agent with real-time token display"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        # Load config from file if it exists
        if config is None:
            config_file = Path("agent_config.json")
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                        file_ops = config_data.get('file_operations', {})
                        config = AgentConfig(
                            lm_studio_url=config_data.get('lm_studio', {}).get('url', 'http://localhost:1234/v1'),
                            model_name=config_data.get('lm_studio', {}).get('model', 'qwen2.5-coder-1.5b-instruct'),
                            temperature=config_data.get('agent_settings', {}).get('temperature', 0.7),
                            max_tokens=config_data.get('agent_settings', {}).get('max_tokens', 4096),
                            stream=config_data.get('agent_settings', {}).get('stream', True),
                            show_token_count=config_data.get('agent_settings', {}).get('show_token_count', True),
                            show_thinking=config_data.get('agent_settings', {}).get('show_thinking', True),
                            plan_mode=file_ops.get('plan_mode', True),
                            allow_file_write=file_ops.get('allow_file_write', True),
                            allow_file_edit=file_ops.get('allow_file_edit', True),
                            allow_file_read=file_ops.get('allow_file_read', True),
                            allowed_directories=file_ops.get('allowed_directories', []),
                            max_file_size_kb=file_ops.get('max_file_size_kb', 500),
                            backup_before_edit=file_ops.get('backup_before_edit', True),
                            overwrite_warning=file_ops.get('overwrite_warning', True)
                        )
                except:
                    config = AgentConfig()
            else:
                config = AgentConfig()
        
        self.config = config
        self.conversation_history: List[Dict[str, str]] = []
        self.workspace = Path(self.config.workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        self.token_count = 0
        self.response_start_time = None
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
        # Initialize conversation with system prompt
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file or use default"""
        prompt_file = Path("system_prompt.txt")
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()
        
        # Default prompt with thinking instructions
        return """⚡ CRITICAL: YOU ARE RUNNING INSIDE A PYTHON AGENT WRAPPER ⚡

You are executing inside coding_agent_streaming.py which:
- PARSES your outputs for [FILE_READ], [FILE_WRITE], [FILE_EDIT], [PLAN] tags
- EXECUTES file operations AUTOMATICALLY when you output these tags
- RETURNS actual file contents/results back to you

This is REAL file system access. DO NOT say "I cannot access files".

ENVIRONMENT:
- MacBook Air M1 (macOS, ARM64)
- Python virtual environment
- Working Directory: ~/Library/Mobile Documents/com~apple~CloudDocs/Claude/Code_Wrapper

FILE OPERATIONS - USE THEM:

**Read files:** Output [FILE_READ]path: ./file.py[/FILE_READ]
**Create files:** First propose [PLAN], then output [FILE_WRITE] after approval
**Modify files:** Output [FILE_EDIT] with find/replace

EXAMPLE CORRECT RESPONSE:
USER: "Can you read the current codebase?"
YOU: "Yes! Let me read the files.

[FILE_READ]
path: ./coding_agent_streaming.py
[/FILE_READ]

I'll analyze it once I see the contents."

EXAMPLE WRONG RESPONSE:
"As a text-based AI, I cannot access files..." ← NEVER say this!

You help build practical software solutions with working, executable code."""
    
    def _stream_response(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Stream response from LM Studio API"""
        self.response_start_time = time.time()
        self.token_count = 0
        
        try:
            response = requests.post(
                f"{self.config.lm_studio_url}/chat/completions",
                json={
                    "model": self.config.model_name,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "stream": True
                },
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    # Parse SSE format
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        
                        if data_str == '[DONE]':
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
                            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot connect to LM Studio at {self.config.lm_studio_url}. "
                f"Error: {str(e)}\n"
                "Please ensure LM Studio is running with the server enabled."
            )
        except Exception as e:
            raise Exception(f"Streaming failed: {str(e)}")
    
    def _make_api_request_no_stream(self, messages: List[Dict[str, str]]) -> str:
        """Make non-streaming request to LM Studio API"""
        try:
            response = requests.post(
                f"{self.config.lm_studio_url}/chat/completions",
                json={
                    "model": self.config.model_name,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _display_thinking(self, text: str, is_thinking: bool = False):
        """Display text with special formatting for thinking sections"""
        if is_thinking:
            # Dim color for thinking
            print(f"\033[90m{text}\033[0m", end="", flush=True)
        else:
            print(text, end="", flush=True)
    
    def process_message_streaming(self, user_message: str) -> str:
        """Process message with streaming response"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        print("\nAgent: ", end="", flush=True)
        
        if self.config.show_token_count:
            print("\033[90m[Generating...]\033[0m ", end="", flush=True)
        
        full_response = ""
        in_thinking = False
        thinking_content = ""
        response_content = ""
        
        try:
            for token in self._stream_response(self.conversation_history):
                full_response += token
                
                # Handle thinking tags
                if self.config.show_thinking:
                    if '[THINKING]' in full_response and not in_thinking:
                        in_thinking = True
                        thinking_start = full_response.index('[THINKING]')
                        pre_thinking = full_response[:thinking_start]
                        if pre_thinking:
                            print(pre_thinking, end="", flush=True)
                        print("\n\033[90m💭 Thinking...\033[0m\n", flush=True)
                        full_response = full_response[thinking_start + len('[THINKING]'):]
                        thinking_content = ""
                    elif '[/THINKING]' in full_response and in_thinking:
                        in_thinking = False
                        thinking_end = full_response.index('[/THINKING]')
                        thinking_content += full_response[:thinking_end]
                        print(f"\033[90m{thinking_content}\033[0m", flush=True)
                        print("\n\033[92m📝 Response:\033[0m\n", flush=True)
                        full_response = full_response[thinking_end + len('[/THINKING]'):]
                        if '[RESPONSE]' in full_response:
                            full_response = full_response[full_response.index('[RESPONSE]') + len('[RESPONSE]'):]
                    elif in_thinking:
                        # Still in thinking mode, don't print yet
                        continue
                    else:
                        # Normal response
                        print(token, end="", flush=True)
                else:
                    # No thinking mode, just stream normally
                    print(token, end="", flush=True)
            
            print()  # New line at end
            
            # Show statistics
            if self.config.show_token_count and self.response_start_time:
                elapsed = time.time() - self.response_start_time
                tokens_per_second = self.token_count / elapsed if elapsed > 0 else 0
                print(f"\n\033[90m[{self.token_count} tokens | {elapsed:.1f}s | {tokens_per_second:.1f} tok/s]\033[0m")
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
            return full_response
            
        except Exception as e:
            # Remove the user message on error
            self.conversation_history.pop()
            print(f"\n\033[91mError: {e}\033[0m")
            raise e
    
    def process_message_no_stream(self, user_message: str) -> str:
        """Process message without streaming"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        print("\nAgent: ", end="", flush=True)
        print("\033[90m[Thinking...]\033[0m", end="", flush=True)
        
        try:
            response = self._make_api_request_no_stream(self.conversation_history)
            
            # Clear the "Thinking..." message
            print("\r" + " " * 50 + "\r", end="")
            print("Agent: ", end="")
            
            # Process thinking tags if present
            if self.config.show_thinking and '[THINKING]' in response:
                parts = response.split('[THINKING]')
                if len(parts) > 1:
                    thinking_parts = parts[1].split('[/THINKING]')
                    if len(thinking_parts) > 1:
                        print("\n\033[90m💭 Thinking:\n" + thinking_parts[0] + "\033[0m\n")
                        actual_response = thinking_parts[1].replace('[RESPONSE]', '').strip()
                        print("\033[92m📝 Response:\033[0m\n" + actual_response)
                    else:
                        print(response)
                else:
                    print(response)
            else:
                print(response)
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            return response
            
        except Exception as e:
            self.conversation_history.pop()
            raise e
    
    def process_message(self, user_message: str) -> str:
        """Process message with plan mode and file operation support"""
        # Get initial response from LLM
        if self.config.stream:
            response = self.process_message_streaming(user_message)
        else:
            response = self.process_message_no_stream(user_message)

        # Check for plan in response
        plan = self.parse_plan(response)

        if plan and self.config.plan_mode:
            # Plan mode is enabled - get user approval
            approval = self.prompt_for_approval(plan)

            if approval == 'reject':
                print("\n\033[91m✗ Plan rejected by user\033[0m")
                # Remove the assistant response from history since it wasn't approved
                if self.conversation_history and self.conversation_history[-1]['role'] == 'assistant':
                    self.conversation_history.pop()
                return "Plan rejected."

            elif approval == 'modify':
                print("\n\033[93mPlease describe the changes you want:\033[0m")
                modifications = input("Modifications: ")
                # Remove the assistant response and add modification request
                if self.conversation_history and self.conversation_history[-1]['role'] == 'assistant':
                    self.conversation_history.pop()
                return self.process_message(f"Modify the previous plan: {modifications}")

            else:  # approved
                print("\n\033[92m✓ Plan approved! Executing...\033[0m")

                # Ask the LLM to execute the plan
                self.conversation_history.append({
                    "role": "user",
                    "content": "The plan has been approved. Now execute the file operations using the [FILE_WRITE], [FILE_EDIT], and [FILE_READ] tags as described in the plan."
                })

                # Get execution response
                if self.config.stream:
                    exec_response = self.process_message_streaming("Execute the approved plan now.")
                else:
                    exec_response = self.process_message_no_stream("Execute the approved plan now.")

                response = exec_response

        # Parse and execute any file operations in the response
        operations = self.parse_file_operations(response)

        if operations:
            print(f"\n\033[96m📁 Found {len(operations)} file operation(s)\033[0m")
            success_count, failure_count = self.execute_file_operations(operations)

            print(f"\n\033[92m✓ Completed: {success_count} successful, {failure_count} failed\033[0m")

        return response
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = [{
            "role": "system",
            "content": self.system_prompt
        }]
        self.token_count = 0
    
    def save_system_prompt(self, prompt: str):
        """Save custom system prompt"""
        with open("system_prompt.txt", 'w') as f:
            f.write(prompt)
        self.system_prompt = prompt
        self.reset_conversation()
        print("\033[92m✓ System prompt updated and conversation reset.\033[0m")
    
    def toggle_streaming(self):
        """Toggle streaming mode"""
        self.config.stream = not self.config.stream
        status = "enabled" if self.config.stream else "disabled"
        print(f"\033[92m✓ Streaming {status}\033[0m")
    
    def toggle_thinking(self):
        """Toggle thinking display"""
        self.config.show_thinking = not self.config.show_thinking
        status = "enabled" if self.config.show_thinking else "disabled"
        print(f"\033[92m✓ Thinking display {status}\033[0m")
    
    def toggle_token_count(self):
        """Toggle token count display"""
        self.config.show_token_count = not self.config.show_token_count
        status = "enabled" if self.config.show_token_count else "disabled"
        print(f"\033[92m✓ Token count display {status}\033[0m")

    def toggle_plan_mode(self):
        """Toggle plan mode"""
        self.config.plan_mode = not self.config.plan_mode
        status = "enabled" if self.config.plan_mode else "disabled"
        print(f"\033[92m✓ Plan mode {status}\033[0m")

    def toggle_file_write(self):
        """Toggle file writing permission"""
        self.config.allow_file_write = not self.config.allow_file_write
        status = "enabled" if self.config.allow_file_write else "disabled"
        print(f"\033[92m✓ File writing {status}\033[0m")

    def _validate_path(self, file_path: str) -> Tuple[bool, str, Path]:
        """Validate file path for security
        Returns: (is_valid, error_message, absolute_path)
        """
        try:
            # Convert to Path object and resolve
            path = Path(file_path).expanduser()

            # Make relative paths absolute based on current working directory
            if not path.is_absolute():
                path = Path.cwd() / path

            path = path.resolve()

            # Check if path is within allowed directories
            if self.config.allowed_directories:
                allowed = False
                for allowed_dir in self.config.allowed_directories:
                    allowed_path = (Path.cwd() / allowed_dir).resolve()
                    try:
                        path.relative_to(allowed_path)
                        allowed = True
                        break
                    except ValueError:
                        continue

                if not allowed:
                    return False, f"Path {path} is not in allowed directories", path

            return True, "", path

        except Exception as e:
            return False, f"Invalid path: {str(e)}", None

    def read_file(self, file_path: str) -> Tuple[bool, str]:
        """Read file contents
        Returns: (success, content_or_error_message)
        """
        if not self.config.allow_file_read:
            return False, "File reading is disabled in configuration"

        is_valid, error, abs_path = self._validate_path(file_path)
        if not is_valid:
            return False, error

        try:
            if not abs_path.exists():
                return False, f"File does not exist: {abs_path}"

            if not abs_path.is_file():
                return False, f"Path is not a file: {abs_path}"

            # Check file size
            size_kb = abs_path.stat().st_size / 1024
            if size_kb > self.config.max_file_size_kb:
                return False, f"File too large: {size_kb:.1f}KB (max: {self.config.max_file_size_kb}KB)"

            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return True, content

        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    def write_file(self, file_path: str, content: str) -> Tuple[bool, str]:
        """Write content to file
        Returns: (success, message)
        """
        if not self.config.allow_file_write:
            return False, "File writing is disabled in configuration"

        is_valid, error, abs_path = self._validate_path(file_path)
        if not is_valid:
            return False, error

        try:
            # Check if file exists and warn
            if abs_path.exists() and self.config.overwrite_warning:
                print(f"\n\033[93m⚠ Warning: File already exists: {abs_path}\033[0m")
                response = input("Overwrite? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    return False, "Write cancelled by user"

            # Check content size
            size_kb = len(content.encode('utf-8')) / 1024
            if size_kb > self.config.max_file_size_kb:
                return False, f"Content too large: {size_kb:.1f}KB (max: {self.config.max_file_size_kb}KB)"

            # Create parent directories if they don't exist
            abs_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, f"Successfully wrote {abs_path} ({len(content)} chars)"

        except Exception as e:
            return False, f"Error writing file: {str(e)}"

    def edit_file(self, file_path: str, find_text: str, replace_text: str) -> Tuple[bool, str]:
        """Edit file by finding and replacing text
        Returns: (success, message)
        """
        if not self.config.allow_file_edit:
            return False, "File editing is disabled in configuration"

        is_valid, error, abs_path = self._validate_path(file_path)
        if not is_valid:
            return False, error

        try:
            if not abs_path.exists():
                return False, f"File does not exist: {abs_path}"

            # Read current content
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Backup if enabled
            if self.config.backup_before_edit:
                backup_path = abs_path.with_suffix(abs_path.suffix + '.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Check if find_text exists
            if find_text not in content:
                return False, f"Text to replace not found in file"

            # Replace text
            new_content = content.replace(find_text, replace_text)

            # Check new content size
            size_kb = len(new_content.encode('utf-8')) / 1024
            if size_kb > self.config.max_file_size_kb:
                return False, f"New content too large: {size_kb:.1f}KB (max: {self.config.max_file_size_kb}KB)"

            # Write modified content
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True, f"Successfully edited {abs_path}"

        except Exception as e:
            return False, f"Error editing file: {str(e)}"

    def parse_plan(self, response: str) -> Optional[str]:
        """Extract plan from [PLAN] tags
        Returns: plan text or None
        """
        if '[PLAN]' not in response or '[/PLAN]' not in response:
            return None

        try:
            start = response.index('[PLAN]') + len('[PLAN]')
            end = response.index('[/PLAN]')
            plan = response[start:end].strip()
            return plan
        except:
            return None

    def parse_file_operations(self, response: str) -> List[Dict[str, Any]]:
        """Extract file operations from response
        Returns: list of operations
        """
        operations = []

        # Parse FILE_WRITE operations
        write_pattern = r'\[FILE_WRITE\](.*?)\[/FILE_WRITE\]'
        for match in re.finditer(write_pattern, response, re.DOTALL):
            op_text = match.group(1)
            # Extract path and content
            path_match = re.search(r'path:\s*(.+?)(?:\n|$)', op_text)
            content_match = re.search(r'content:\s*```(?:\w+)?\n(.*?)```', op_text, re.DOTALL)

            if path_match and content_match:
                operations.append({
                    'type': 'write',
                    'path': path_match.group(1).strip(),
                    'content': content_match.group(1)
                })

        # Parse FILE_EDIT operations
        edit_pattern = r'\[FILE_EDIT\](.*?)\[/FILE_EDIT\]'
        for match in re.finditer(edit_pattern, response, re.DOTALL):
            op_text = match.group(1)
            path_match = re.search(r'path:\s*(.+?)(?:\n|$)', op_text)
            find_match = re.search(r'find:\s*\|\n(.*?)\nreplace:', op_text, re.DOTALL)
            replace_match = re.search(r'replace:\s*\|\n(.*?)(?:\n\[|$)', op_text, re.DOTALL)

            if path_match and find_match and replace_match:
                operations.append({
                    'type': 'edit',
                    'path': path_match.group(1).strip(),
                    'find': find_match.group(1),
                    'replace': replace_match.group(1)
                })

        # Parse FILE_READ operations
        read_pattern = r'\[FILE_READ\](.*?)\[/FILE_READ\]'
        for match in re.finditer(read_pattern, response, re.DOTALL):
            op_text = match.group(1)
            path_match = re.search(r'path:\s*(.+?)(?:\n|$)', op_text)

            if path_match:
                operations.append({
                    'type': 'read',
                    'path': path_match.group(1).strip()
                })

        return operations

    def prompt_for_approval(self, plan: str) -> str:
        """Show plan and get user approval
        Returns: 'approve', 'modify', or 'reject'
        """
        print("\n" + "=" * 60)
        print("\033[96m📋 PLAN PROPOSED\033[0m")
        print("=" * 60)
        print(plan)
        print("=" * 60)

        while True:
            response = input("\n\033[93mApprove this plan?\033[0m (yes/no/modify): ").strip().lower()
            if response in ['yes', 'y', 'approve']:
                return 'approve'
            elif response in ['no', 'n', 'reject']:
                return 'reject'
            elif response in ['modify', 'm', 'change']:
                return 'modify'
            else:
                print("\033[91mPlease enter 'yes', 'no', or 'modify'\033[0m")

    def execute_file_operations(self, operations: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Execute approved file operations
        Returns: (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0

        for op in operations:
            op_type = op['type']
            path = op['path']

            print(f"\n\033[94m→ Executing: {op_type.upper()} {path}\033[0m")

            if op_type == 'write':
                success, message = self.write_file(path, op['content'])
            elif op_type == 'edit':
                success, message = self.edit_file(path, op['find'], op['replace'])
            elif op_type == 'read':
                success, content = self.read_file(path)
                if success:
                    print(f"\033[90m--- File Content ({len(content)} chars) ---\033[0m")
                    print(content[:500] + ("..." if len(content) > 500 else ""))
                    message = f"Successfully read {path}"
                else:
                    message = content

            if success:
                print(f"\033[92m✓ {message}\033[0m")
                success_count += 1
            else:
                print(f"\033[91m✗ {message}\033[0m")
                failure_count += 1

        return success_count, failure_count


def main():
    """Interactive CLI for the streaming agent"""
    print("=" * 60)
    print("Qwen2.5-Coder Agent via LM Studio (Streaming)")
    print("AI Coding Assistant - POC Development")
    print("=" * 60)
    print("\nCommands:")
    print("  /help        - Show this help")
    print("  /reset       - Reset conversation")
    print("  /config      - Show configuration")
    print("  /stream      - Toggle streaming on/off")
    print("  /thinking    - Toggle thinking display on/off")
    print("  /tokens      - Toggle token count display on/off")
    print("  /plan        - Toggle plan mode on/off")
    print("  /allow_write - Toggle file writing permission")
    print("  /read <file> - Read a file")
    print("  /ls [path]   - List files in directory")
    print("  /prompt      - Edit system prompt")
    print("  /save_prompt - Save current prompt to file")
    print("  /exit        - Exit agent")
    print("\nType your message or command...\n")
    
    # Initialize agent
    agent = StreamingAgent()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.startswith('/'):
                # Handle commands
                command = user_input[1:].lower().split()[0]
                
                if command == 'exit':
                    print("Goodbye!")
                    break
                elif command == 'help':
                    print("\nCommands:")
                    print("  /help        - Show this help")
                    print("  /reset       - Reset conversation")
                    print("  /config      - Show configuration")
                    print("  /stream      - Toggle streaming on/off")
                    print("  /thinking    - Toggle thinking display on/off")
                    print("  /tokens      - Toggle token count display on/off")
                    print("  /plan        - Toggle plan mode on/off")
                    print("  /allow_write - Toggle file writing permission")
                    print("  /read <file> - Read a file")
                    print("  /ls [path]   - List files in directory")
                    print("  /prompt      - Edit system prompt")
                    print("  /save_prompt - Save current prompt to file")
                    print("  /exit        - Exit agent")
                elif command == 'reset':
                    agent.reset_conversation()
                    print("\033[92m✓ Conversation reset.\033[0m")
                elif command == 'config':
                    print(f"\nConfiguration:")
                    print(f"  URL: {agent.config.lm_studio_url}")
                    print(f"  Model: {agent.config.model_name}")
                    print(f"  Temperature: {agent.config.temperature}")
                    print(f"  Max tokens: {agent.config.max_tokens}")
                    print(f"  Streaming: {agent.config.stream}")
                    print(f"  Show thinking: {agent.config.show_thinking}")
                    print(f"  Show tokens: {agent.config.show_token_count}")
                    print(f"  Plan mode: {agent.config.plan_mode}")
                    print(f"  File write: {agent.config.allow_file_write}")
                    print(f"  File edit: {agent.config.allow_file_edit}")
                    print(f"  File read: {agent.config.allow_file_read}")
                elif command == 'stream':
                    agent.toggle_streaming()
                elif command == 'thinking':
                    agent.toggle_thinking()
                elif command == 'tokens':
                    agent.toggle_token_count()
                elif command == 'plan':
                    agent.toggle_plan_mode()
                elif command == 'allow_write':
                    agent.toggle_file_write()
                elif command == 'read':
                    # Extract file path from command
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        print("\033[91mUsage: /read <file_path>\033[0m")
                    else:
                        file_path = parts[1]
                        success, result = agent.read_file(file_path)
                        if success:
                            print(f"\n\033[92m--- {file_path} ---\033[0m")
                            print(result)
                            print("\033[92m" + "-" * 40 + "\033[0m")
                        else:
                            print(f"\033[91m✗ {result}\033[0m")
                elif command == 'ls':
                    # List files in directory
                    parts = user_input.split(maxsplit=1)
                    dir_path = parts[1] if len(parts) > 1 else '.'
                    try:
                        path = Path(dir_path).expanduser()
                        if not path.is_absolute():
                            path = Path.cwd() / path
                        path = path.resolve()

                        if path.is_dir():
                            files = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
                            print(f"\n\033[92m--- Contents of {path} ---\033[0m")
                            for item in files:
                                if item.is_dir():
                                    print(f"  📁 {item.name}/")
                                else:
                                    size_kb = item.stat().st_size / 1024
                                    print(f"  📄 {item.name} ({size_kb:.1f} KB)")
                            print(f"\033[92mTotal: {len(files)} items\033[0m")
                        else:
                            print(f"\033[91m✗ Not a directory: {path}\033[0m")
                    except Exception as e:
                        print(f"\033[91m✗ Error: {str(e)}\033[0m")
                elif command == 'prompt':
                    print("\nCurrent system prompt:")
                    print("-" * 40)
                    print(agent.system_prompt)
                    print("-" * 40)
                    print("\nEnter new prompt (type END on a new line when done):")
                    lines = []
                    while True:
                        line = input()
                        if line == 'END':
                            break
                        lines.append(line)
                    new_prompt = '\n'.join(lines)
                    if new_prompt:
                        agent.save_system_prompt(new_prompt)
                elif command == 'save_prompt':
                    agent.save_system_prompt(agent.system_prompt)
                else:
                    print(f"Unknown command: /{command}")
            else:
                # Process message
                agent.process_message(user_input)
                
        except KeyboardInterrupt:
            print("\n\n\033[93mInterrupted. Type /exit to quit.\033[0m")
        except ConnectionError as e:
            print(f"\n\033[91mConnection Error: {e}\033[0m")
        except Exception as e:
            print(f"\n\033[91mError: {e}\033[0m")


if __name__ == "__main__":
    main()
