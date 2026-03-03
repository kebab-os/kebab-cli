"""Main terminal emulator logic"""

import os
import subprocess
import sys

import pygame

from .config import TERM_CONFIG
from .buffer import TerminalBuffer, InputBuffer
from .commands import CommandRegistry
from .utils import parse_command, strip_ansi


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
        # Selection state: anchor and cursor are position dicts {'type':'output'|'input','line':int,'char':int}
        self.selection_active = False
        self.selection_anchor = None
        self.selection_cursor = None
        self.selecting = False
        
    def get_prompt(self):
        """Generate bash-style prompt"""
        home = str(os.path.expanduser('~'))
        display_path = self.cwd.replace(home, '~')
        return f"{self.user}@{self.hostname}:{display_path}$ "
    
    def execute_command(self, cmd_line):
        """Execute a command line"""
        # Always echo the prompt+line to the output (even if empty)
        self.output_buffer.add(self.get_prompt() + cmd_line, TERM_CONFIG['prompt_color'])
        if not cmd_line.strip():
            # don't add empty input to history or run anything
            return

        self.input_buffer.add_to_history(cmd_line)
        
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
        shift = mods & (pygame.KMOD_SHIFT | pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)
        ctrl = mods & (pygame.KMOD_CTRL | pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)
        alt = mods & (pygame.KMOD_ALT | pygame.KMOD_LALT | pygame.KMOD_RALT)
        
        key = event.key
        
        # Ctrl+C - Copy selection or Cancel/Interrupt
        if ctrl and key == pygame.K_c:
            sel = self.get_selection()
            if sel:
                # copy selected text
                from .utils import clipboard_copy
                txt = self.get_selection_text()
                clipboard_copy(txt)
                return
            # no selection -> original behavior
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
            # Shift+Left extends selection
            if shift:
                prev_pos = self.input_buffer.cursor_pos
                self.input_buffer.move_cursor_left(word=alt)
                self._update_input_selection(prev_pos, self.input_buffer.cursor_pos)
            else:
                self.input_buffer.move_cursor_left(word=alt)
                self.clear_selection()
        elif key == pygame.K_RIGHT or (ctrl and key == pygame.K_f):
            if shift:
                prev_pos = self.input_buffer.cursor_pos
                self.input_buffer.move_cursor_right(word=alt)
                self._update_input_selection(prev_pos, self.input_buffer.cursor_pos)
            else:
                self.input_buffer.move_cursor_right(word=alt)
                self.clear_selection()
            
        # History
        elif key == pygame.K_UP or (ctrl and key == pygame.K_p):
            self.input_buffer.history_prev()
        elif key == pygame.K_DOWN or (ctrl and key == pygame.K_n):
            self.input_buffer.history_next()
            
        # Editing
        elif key == pygame.K_BACKSPACE:
            # delete selection if present
            if self.selection_active:
                self.delete_selection()
            else:
                if alt or ctrl:
                    self.input_buffer.delete_word_backward()
                else:
                    self.input_buffer.backspace()
        elif key == pygame.K_DELETE:
            if self.selection_active:
                self.delete_selection()
            else:
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
            self.clear_selection()
            
        # Tab
        elif key == pygame.K_TAB:
            self.input_buffer.insert('    ')
            
        # Regular text input
        elif not ctrl and not alt and event.unicode:
            if event.unicode.isprintable():
                # if a selection exists, replace it with the new character
                if self.selection_active:
                    self.replace_selection_with_text(event.unicode)
                else:
                    self.input_buffer.insert(event.unicode)

        # Clipboard shortcuts: Ctrl+X cut, Ctrl+V paste
        if ctrl and key == pygame.K_x:
            sel = self.get_selection()
            if sel:
                from .utils import clipboard_copy
                txt = self.get_selection_text()
                clipboard_copy(txt)
                self.delete_selection()
            return

        if ctrl and key == pygame.K_v:
            from .utils import clipboard_paste
            txt = clipboard_paste()
            if not txt:
                return
            # replace selection or insert at cursor
            if self.selection_active:
                self.delete_selection()
            # insert text into input buffer at cursor
            for ch in txt:
                if ch == '\n':
                    # treat newline as executing current input and starting new line
                    cmd = self.input_buffer.get_text()
                    self.input_buffer.buffer.clear()
                    self.input_buffer.cursor_pos = 0
                    self.execute_command(cmd)
                else:
                    self.input_buffer.insert(ch)
            return
    
    def update_cursor(self, dt):
        """Update cursor blink state"""
        self.last_blink += dt
        if self.last_blink >= TERM_CONFIG['cursor_blink_ms']:
            self.last_blink = 0
            self.cursor_visible = not self.cursor_visible

    def _update_input_selection(self, anchor_pos, cursor_pos):
        """Internal: set or update selection within input line."""
        # anchor_pos is the previous cursor; if no active selection, set anchor to that
        if not self.selection_active:
            self.selection_active = True
            self.selection_anchor = {'type': 'input', 'line': None, 'char': anchor_pos}
        self.selection_cursor = {'type': 'input', 'line': None, 'char': cursor_pos}

    def get_selection_text(self):
        """Return the currently selected text (or empty string)."""
        sel = self.get_selection()
        if not sel:
            return ''
        a, b = sel
        # both input
        if a['type'] == 'input' and b['type'] == 'input':
            s = a['char']
            e = b['char']
            return ''.join(self.input_buffer.buffer[s:e])

        # both output
        if a['type'] == 'output' and b['type'] == 'output':
            lines = self.output_buffer.lines
            parts = []
            for ln in range(a['line'], b['line'] + 1):
                txt = strip_ansi(lines[ln]['text'])
                if ln == a['line'] and ln == b['line']:
                    parts.append(txt[a['char']:b['char']])
                elif ln == a['line']:
                    parts.append(txt[a['char']:])
                elif ln == b['line']:
                    parts.append(txt[:b['char']])
                else:
                    parts.append(txt)
            return '\n'.join(parts)

        # mixed: output then input (a is output, b is input)
        if a['type'] == 'output' and b['type'] == 'input':
            lines = self.output_buffer.lines
            parts = []
            for ln in range(a['line'], len(lines)):
                txt = strip_ansi(lines[ln]['text'])
                if ln == a['line']:
                    parts.append(txt[a['char']:])
                else:
                    parts.append(txt)
            input_part = ''.join(self.input_buffer.buffer[:b['char']])
            parts.append(input_part)
            return '\n'.join(parts)
        return ''

    def delete_selection(self):
        """Delete the currently active selection from buffers and set cursor."""
        sel = self.get_selection()
        if not sel:
            return
        a, b = sel
        # input only
        if a['type'] == 'input' and b['type'] == 'input':
            s = a['char']
            e = b['char']
            del self.input_buffer.buffer[s:e]
            self.input_buffer.cursor_pos = s
            self.clear_selection()
            return

        # output only
        if a['type'] == 'output' and b['type'] == 'output':
            lines = self.output_buffer.lines
            first = lines[a['line']]['text']
            last = lines[b['line']]['text']
            first_left = first[:a['char']]
            last_right = last[b['char']:]
            new_text = first_left + last_right
            # replace first line and delete middle+last
            lines[a['line']]['text'] = new_text
            del lines[a['line']+1:b['line']+1]
            self.clear_selection()
            return

        # mixed selection (output -> input): delete tail of output and head of input
        if a['type'] == 'output' and b['type'] == 'input':
            lines = self.output_buffer.lines
            first = strip_ansi(lines[a['line']]['text'])
            left = first[:a['char']]
            # set first line to left and remove all following output lines (they were selected)
            lines[a['line']]['text'] = left
            del lines[a['line']+1:]
            # remove selected portion from input (head up to b['char'])
            del self.input_buffer.buffer[:b['char']]
            self.input_buffer.cursor_pos = 0
            self.clear_selection()
            return

    def replace_selection_with_text(self, text):
        # delete selection then insert text into input
        if self.selection_active:
            self.delete_selection()
        for ch in text:
            if ch == '\n':
                cmd = self.input_buffer.get_text()
                self.input_buffer.buffer.clear()
                self.input_buffer.cursor_pos = 0
                self.execute_command(cmd)
            else:
                self.input_buffer.insert(ch)

    def start_selection(self, pos):
        self.selection_active = True
        self.selection_anchor = pos
        self.selection_cursor = pos
        self.selecting = True

    def update_selection(self, pos):
        if not self.selection_active:
            self.start_selection(pos)
        else:
            self.selection_cursor = pos

    def end_selection(self):
        # stop interactive selecting but keep selection available
        self.selecting = False

    def clear_selection(self):
        self.selection_active = False
        self.selection_anchor = None
        self.selection_cursor = None

    def get_selection(self):
        if not self.selection_active or not self.selection_anchor or not self.selection_cursor:
            return None
        a = self.selection_anchor
        b = self.selection_cursor
        # Normalize order: compare tuples (type, line, char) where output lines use (line,char) and input uses (inf, char)
        if a['type'] == b['type'] == 'output':
            if (a['line'], a['char']) <= (b['line'], b['char']):
                return (a, b)
            else:
                return (b, a)
        if a['type'] == b['type'] == 'input':
            if a['char'] <= b['char']:
                return (a, b)
            else:
                return (b, a)
        # If mixed types, order by type: output before input
        if a['type'] == 'output' and b['type'] == 'input':
            return (a, b)
        return (b, a)
