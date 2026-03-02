"""Main terminal emulator logic"""

import os
import subprocess
import sys

import pygame

from .config import TERM_CONFIG
from .buffer import TerminalBuffer, InputBuffer
from .commands import CommandRegistry
from .utils import parse_command


class TerminalEmulator:
    """Main terminal emulator class"""
    
    def __init__(self):
        self.cwd = os.getcwd()
        self.user = os.getenv('USER', os.getenv('USERNAME', 'user'))
        self.hostname = os.getenv('COMPUTERNAME', 'kebab-os')
        self.input_buffer = InputBuffer()
        self.output_buffer = TerminalBuffer(TERM_CONFIG['scrollback_lines'])
        self.command_registry = CommandRegistry(self)
        self.running = True
        self.cursor_visible = True
        self.last_blink = 0
        
    def get_prompt(self):
        """Generate bash-style prompt"""
        home = str(os.path.expanduser('~'))
        display_path = self.cwd.replace(home, '~')
        return f"{self.user}@{self.hostname}:{display_path}$ "
    
    def execute_command(self, cmd_line):
        """Execute a command line"""
        if not cmd_line.strip():
            return
            
        self.input_buffer.add_to_history(cmd_line)
        self.output_buffer.add(self.get_prompt() + cmd_line, TERM_CONFIG['prompt_color'])
        
        parts = parse_command(cmd_line)
        if not parts:
            return
            
        cmd = parts[0]
        args = parts[1:]
        
        # Check for builtins
        handler = self.command_registry.get(cmd)
        if handler:
            try:
                handler(args)
            except Exception as e:
                self.output_buffer.add(f"Error: {e}", TERM_CONFIG['error_color'])
        else:
            self.run_external(cmd, args)
            
    def run_external(self, cmd, args):
        """Run external system command"""
        try:
            env = os.environ.copy()
            env['PWD'] = self.cwd
            
            result = subprocess.run(
                [cmd] + args,
                capture_output=True,
                text=True,
                cwd=self.cwd,
                env=env,
                timeout=30
            )
            
            if result.stdout:
                self.output_buffer.add(result.stdout.rstrip())
            if result.stderr:
                self.output_buffer.add(result.stderr.rstrip(), TERM_CONFIG['error_color'])
                
        except FileNotFoundError:
            self.output_buffer.add(f"Command not found: {cmd}", TERM_CONFIG['error_color'])
        except subprocess.TimeoutExpired:
            self.output_buffer.add(f"Command timed out: {cmd}", TERM_CONFIG['error_color'])
        except Exception as e:
            self.output_buffer.add(f"Error executing {cmd}: {e}", TERM_CONFIG['error_color'])
    
    def handle_key(self, event):
        """Handle keyboard input with full readline shortcuts"""
        mods = event.mod
        ctrl = mods & (pygame.KMOD_CTRL | pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)
        alt = mods & (pygame.KMOD_ALT | pygame.KMOD_LALT | pygame.KMOD_RALT)
        
        key = event.key
        
        # Ctrl+C - Cancel/Interrupt
        if ctrl and key == pygame.K_c:
            self.output_buffer.add("^C", TERM_CONFIG['error_color'])
            self.input_buffer.buffer.clear()
            self.input_buffer.cursor_pos = 0
            return
            
        # Ctrl+L - Clear screen
        if ctrl and key == pygame.K_l:
            self.command_registry.cmd_clear([])
            return
            
        # Ctrl+D - EOF/Delete
        if ctrl and key == pygame.K_d:
            if not self.input_buffer.buffer:
                self.running = False
            else:
                self.input_buffer.delete()
            return
        
        # Navigation
        if key == pygame.K_HOME or (ctrl and key == pygame.K_a):
            self.input_buffer.move_to_start()
        elif key == pygame.K_END or (ctrl and key == pygame.K_e):
            self.input_buffer.move_to_end()
        elif key == pygame.K_LEFT or (ctrl and key == pygame.K_b):
            self.input_buffer.move_cursor_left(word=alt)
        elif key == pygame.K_RIGHT or (ctrl and key == pygame.K_f):
            self.input_buffer.move_cursor_right(word=alt)
            
        # History
        elif key == pygame.K_UP or (ctrl and key == pygame.K_p):
            self.input_buffer.history_prev()
        elif key == pygame.K_DOWN or (ctrl and key == pygame.K_n):
            self.input_buffer.history_next()
            
        # Editing
        elif key == pygame.K_BACKSPACE:
            if alt or ctrl:
                self.input_buffer.delete_word_backward()
            else:
                self.input_buffer.backspace()
        elif key == pygame.K_DELETE:
            self.input_buffer.delete()
        elif ctrl and key == pygame.K_w:
            self.input_buffer.delete_word_backward()
        elif alt and key == pygame.K_d:
            self.input_buffer.delete_word_forward()
        elif ctrl and key == pygame.K_u:
            self.input_buffer.delete_to_start()
        elif ctrl and key == pygame.K_k:
            self.input_buffer.delete_to_end()
        elif ctrl and key == pygame.K_t:
            self.input_buffer.swap_chars()
            
        # Case changes
        elif alt and key == pygame.K_u:
            self.input_buffer.upcase_word()
        elif alt and key == pygame.K_l:
            self.input_buffer.downcase_word()
        elif alt and key == pygame.K_c:
            self.input_buffer.capitalize_word()
            
        # Enter
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            cmd = self.input_buffer.get_text()
            self.input_buffer.buffer.clear()
            self.input_buffer.cursor_pos = 0
            self.execute_command(cmd)
            
        # Tab
        elif key == pygame.K_TAB:
            self.input_buffer.insert('    ')
            
        # Regular text input
        elif not ctrl and not alt and event.unicode:
            if event.unicode.isprintable():
                self.input_buffer.insert(event.unicode)
    
    def update_cursor(self, dt):
        """Update cursor blink state"""
        self.last_blink += dt
        if self.last_blink >= TERM_CONFIG['cursor_blink_ms']:
            self.last_blink = 0
            self.cursor_visible = not self.cursor_visible
