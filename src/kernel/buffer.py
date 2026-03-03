"""Terminal and input buffer management"""

from .config import TERM_CONFIG


class TerminalBuffer:
    """Manages terminal output lines with scrollback"""
    
    def __init__(self, max_lines=500):
        self.lines = []
        self.max_lines = max_lines
        self.scroll_offset = 0
        
    def add(self, text, color=None):
        """Add a line to the buffer"""
        for line in str(text).split('\n'):
            self.lines.append({'text': line, 'color': color})
        while len(self.lines) > self.max_lines:
            self.lines.pop(0)
        self.scroll_offset = 0
        
    def get_visible(self, height, line_height):
        """Get lines visible in the current viewport"""
        max_visible = height // line_height
        start = max(0, len(self.lines) - max_visible - self.scroll_offset)
        end = min(len(self.lines), start + max_visible)
        return self.lines[start:end]

    def get_visible_with_start(self, height, line_height):
        """Return (visible_lines, start_index) so callers can map visible indices to absolute lines."""
        max_visible = height // line_height
        start = max(0, len(self.lines) - max_visible - self.scroll_offset)
        end = min(len(self.lines), start + max_visible)
        return (self.lines[start:end], start)
    
    def scroll_up(self, lines=3):
        self.scroll_offset = min(len(self.lines), self.scroll_offset + lines)
    
    def scroll_down(self, lines=3):
        self.scroll_offset = max(0, self.scroll_offset - lines)
    
    def clear(self):
        self.lines.clear()
        self.scroll_offset = 0


class InputBuffer:
    """Manages the current input line with full readline-style editing"""
    
    def __init__(self):
        self.buffer = []
        self.cursor_pos = 0
        self.history = []
        self.history_index = -1
        self.saved_input = ""
        
    def insert(self, char):
        """Insert character at cursor position"""
        self.buffer.insert(self.cursor_pos, char)
        self.cursor_pos += 1
        
    def backspace(self):
        """Delete character before cursor"""
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
            del self.buffer[self.cursor_pos]
            
    def delete(self):
        """Delete character at cursor"""
        if self.cursor_pos < len(self.buffer):
            del self.buffer[self.cursor_pos]
            
    def delete_word_backward(self):
        """Delete word before cursor (Ctrl+W)"""
        if self.cursor_pos == 0:
            return
        pos = self.cursor_pos - 1
        while pos > 0 and self.buffer[pos].isspace():
            pos -= 1
        while pos > 0 and not self.buffer[pos-1].isspace():
            pos -= 1
        del self.buffer[pos:self.cursor_pos]
        self.cursor_pos = pos
        
    def delete_word_forward(self):
        """Delete word after cursor (Alt+D)"""
        if self.cursor_pos >= len(self.buffer):
            return
        pos = self.cursor_pos
        while pos < len(self.buffer) and self.buffer[pos].isspace():
            pos += 1
        while pos < len(self.buffer) and not self.buffer[pos].isspace():
            pos += 1
        del self.buffer[self.cursor_pos:pos]
        
    def delete_to_start(self):
        """Delete from cursor to start (Ctrl+U)"""
        del self.buffer[:self.cursor_pos]
        self.cursor_pos = 0
        
    def delete_to_end(self):
        """Delete from cursor to end (Ctrl+K)"""
        del self.buffer[self.cursor_pos:]
        
    def move_cursor_left(self, word=False):
        """Move cursor left"""
        if word:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                while self.cursor_pos > 0 and self.buffer[self.cursor_pos-1].isspace():
                    self.cursor_pos -= 1
                while self.cursor_pos > 0 and not self.buffer[self.cursor_pos-1].isspace():
                    self.cursor_pos -= 1
        else:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                
    def move_cursor_right(self, word=False):
        """Move cursor right"""
        if word:
            if self.cursor_pos < len(self.buffer):
                while self.cursor_pos < len(self.buffer) and not self.buffer[self.cursor_pos].isspace():
                    self.cursor_pos += 1
                while self.cursor_pos < len(self.buffer) and self.buffer[self.cursor_pos].isspace():
                    self.cursor_pos += 1
        else:
            if self.cursor_pos < len(self.buffer):
                self.cursor_pos += 1
                
    def move_to_start(self):
        """Move cursor to start of line"""
        self.cursor_pos = 0
        
    def move_to_end(self):
        """Move cursor to end of line"""
        self.cursor_pos = len(self.buffer)
        
    def swap_chars(self):
        """Swap current and previous character (Ctrl+T)"""
        if self.cursor_pos > 0 and self.cursor_pos < len(self.buffer):
            self.buffer[self.cursor_pos-1], self.buffer[self.cursor_pos] = \
                self.buffer[self.cursor_pos], self.buffer[self.cursor_pos-1]
            self.cursor_pos += 1
            
    def upcase_word(self):
        """Uppercase current word (Alt+U)"""
        pos = self.cursor_pos
        while pos < len(self.buffer) and self.buffer[pos].isspace():
            pos += 1
        while pos < len(self.buffer) and not self.buffer[pos].isspace():
            self.buffer[pos] = self.buffer[pos].upper()
            pos += 1
            
    def downcase_word(self):
        """Lowercase current word (Alt+L)"""
        pos = self.cursor_pos
        while pos < len(self.buffer) and self.buffer[pos].isspace():
            pos += 1
        while pos < len(self.buffer) and not self.buffer[pos].isspace():
            self.buffer[pos] = self.buffer[pos].lower()
            pos += 1
            
    def capitalize_word(self):
        """Capitalize current word (Alt+C)"""
        pos = self.cursor_pos
        while pos < len(self.buffer) and self.buffer[pos].isspace():
            pos += 1
        if pos < len(self.buffer):
            self.buffer[pos] = self.buffer[pos].upper()
            pos += 1
        while pos < len(self.buffer) and not self.buffer[pos].isspace():
            self.buffer[pos] = self.buffer[pos].lower()
            pos += 1
    
    def get_text(self):
        return ''.join(self.buffer)
    
    def set_text(self, text):
        self.buffer = list(text)
        self.cursor_pos = len(self.buffer)
        
    def history_prev(self):
        """Previous history item"""
        if self.history_index == -1:
            self.saved_input = self.get_text()
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.set_text(self.history[-(self.history_index+1)])
            
    def history_next(self):
        """Next history item"""
        if self.history_index > 0:
            self.history_index -= 1
            self.set_text(self.history[-(self.history_index+1)])
        elif self.history_index == 0:
            self.history_index = -1
            self.set_text(self.saved_input)
            
    def add_to_history(self, cmd):
        if cmd.strip():
            self.history.append(cmd)
            if len(self.history) > TERM_CONFIG['max_history']:
                self.history.pop(0)
        self.history_index = -1
        self.saved_input = ""
