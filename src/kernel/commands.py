"""Built-in command implementations"""

import os
import sys
from datetime import datetime
from pathlib import Path

from .config import TERM_CONFIG


class CommandRegistry:
    """Registry and executor for built-in commands"""
    
    def __init__(self, terminal):
        self.terminal = terminal
        self.commands = {
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'help': self.cmd_help,
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'ls': self.cmd_ls,
            'echo': self.cmd_echo,
            'history': self.cmd_history,
            'whoami': self.cmd_whoami,
            'date': self.cmd_date,
            'neofetch': self.cmd_neofetch,
            'mkdir': self.cmd_mkdir,
            'touch': self.cmd_touch,
            'rm': self.cmd_rm,
            'cat': self.cmd_cat,
        }
    
    def get(self, name):
        return self.commands.get(name)
    
    def cmd_clear(self, args):
        self.terminal.output_buffer.clear()
        
    def cmd_exit(self, args):
        self.terminal.running = False
        
    def cmd_help(self, args):
        help_text = """Kebab-CLI v1.0 - Available Commands:
Builtins: clear, exit, help, cd, pwd, ls, echo, history, whoami, date, neofetch, mkdir, touch, rm, cat

Keyboard Shortcuts:
  Ctrl+A/Home  - Start of line    Ctrl+E/End   - End of line
  Ctrl+B/←     - Move left        Ctrl+F/→     - Move right
  Alt+B        - Word back        Alt+F        - Word forward
  Ctrl+D/Del   - Delete char      Backspace    - Delete back
  Ctrl+W       - Delete word back Alt+D        - Delete word forward
  Ctrl+U       - Delete to start  Ctrl+K       - Delete to end
  Ctrl+P/↑     - History prev     Ctrl+N/↓     - History next
  Ctrl+L       - Clear screen     Ctrl+C       - Cancel line
  Ctrl+T       - Swap chars       Tab          - Auto-complete
  Alt+U        - Uppercase word   Alt+L        - Lowercase word
  Alt+C        - Capitalize word"""
        self.terminal.output_buffer.add(help_text, TERM_CONFIG['success_color'])
        
    def cmd_cd(self, args):
        path = args[0] if args else str(Path.home())
        try:
            new_path = os.path.abspath(os.path.join(self.terminal.cwd, os.path.expanduser(path)))
            os.chdir(new_path)
            self.terminal.cwd = new_path
        except Exception as e:
            self.terminal.output_buffer.add(f"cd: {e}", TERM_CONFIG['error_color'])
            
    def cmd_pwd(self, args):
        self.terminal.output_buffer.add(self.terminal.cwd)
        
    def cmd_ls(self, args):
        try:
            items = os.listdir(self.terminal.cwd)
            show_all = '-a' in args or '-la' in args or '-al' in args
            long_format = '-l' in args or '-la' in args or '-al' in args
            
            if show_all:
                items = ['.', '..'] + sorted(items)
            else:
                items = [i for i in items if not i.startswith('.')]
                items.sort()
            
            if long_format:
                for item in items:
                    full_path = os.path.join(self.terminal.cwd, item)
                    stat = os.stat(full_path)
                    perms = self._format_perms(stat.st_mode)
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%b %d %H:%M")
                    self.terminal.output_buffer.add(f"{perms} {size:>8} {mtime} {item}")
            else:
                # Color coding for simple ls
                output = []
                for item in items:
                    full_path = os.path.join(self.terminal.cwd, item)
                    if os.path.isdir(full_path):
                        output.append(f"\033[1;34m{item}/\033[0m")
                    elif os.access(full_path, os.X_OK):
                        output.append(f"\033[1;32m{item}*\033[0m")
                    else:
                        output.append(item)
                self.terminal.output_buffer.add('  '.join(output))
        except Exception as e:
            self.terminal.output_buffer.add(f"ls: {e}", TERM_CONFIG['error_color'])
    
    def _format_perms(self, mode):
        """Format file permissions like ls -l"""
        perms = ['-'] * 10
        if mode & 0o040000: perms[0] = 'd'
        elif mode & 0o100000: perms[0] = '-'
        
        # Owner
        perms[1] = 'r' if mode & 0o400 else '-'
        perms[2] = 'w' if mode & 0o200 else '-'
        perms[3] = 'x' if mode & 0o100 else '-'
        # Group
        perms[4] = 'r' if mode & 0o040 else '-'
        perms[5] = 'w' if mode & 0o020 else '-'
        perms[6] = 'x' if mode & 0o010 else '-'
        # Other
        perms[7] = 'r' if mode & 0o004 else '-'
        perms[8] = 'w' if mode & 0o002 else '-'
        perms[9] = 'x' if mode & 0o001 else '-'
        
        return ''.join(perms)
            
    def cmd_echo(self, args):
        self.terminal.output_buffer.add(' '.join(args))
        
    def cmd_history(self, args):
        for i, cmd in enumerate(self.terminal.input_buffer.history, 1):
            self.terminal.output_buffer.add(f"  {i}  {cmd}")
            
    def cmd_whoami(self, args):
        self.terminal.output_buffer.add(self.terminal.user)
        
    def cmd_date(self, args):
        self.terminal.output_buffer.add(datetime.now().strftime("%a %b %d %H:%M:%S %Y"))
        
    def cmd_neofetch(self, args):
        ascii_art = r"""
    ___  ________________  ___    ____  __    ________ 
   / _ \/ ___/ ___/ __/ / / / |  / / / / /   / ____/ / 
  / // / /__/ /__/ _// /_/ /| | / / /_/ /   / /   / /  
 /____/\___/\___/___/\__,_/ |___/\____/   /_/   /_/   
                                                       """
        info = f"""
{ascii_art}
OS: Kebab-CLI v1.0 (Pygame Terminal)
Shell: kebab-sh
User: {self.terminal.user}
Hostname: {self.terminal.hostname}
CWD: {self.terminal.cwd}
Python: {sys.version.split()[0]}
Pygame: {__import__('pygame').version.ver}
        """
        self.terminal.output_buffer.add(info, TERM_CONFIG['success_color'])
    
    def cmd_mkdir(self, args):
        if not args:
            self.terminal.output_buffer.add("mkdir: missing operand", TERM_CONFIG['error_color'])
            return
        for path in args:
            try:
                os.makedirs(os.path.join(self.terminal.cwd, path), exist_ok=True)
            except Exception as e:
                self.terminal.output_buffer.add(f"mkdir: cannot create directory '{path}': {e}", TERM_CONFIG['error_color'])
    
    def cmd_touch(self, args):
        if not args:
            self.terminal.output_buffer.add("touch: missing file operand", TERM_CONFIG['error_color'])
            return
        for path in args:
            try:
                full_path = os.path.join(self.terminal.cwd, path)
                if os.path.exists(full_path):
                    os.utime(full_path, None)
                else:
                    open(full_path, 'a').close()
            except Exception as e:
                self.terminal.output_buffer.add(f"touch: cannot touch '{path}': {e}", TERM_CONFIG['error_color'])
    
    def cmd_rm(self, args):
        if not args:
            self.terminal.output_buffer.add("rm: missing operand", TERM_CONFIG['error_color'])
            return
        recursive = '-r' in args or '-rf' in args
        force = '-f' in args or '-rf' in args
        targets = [a for a in args if not a.startswith('-')]
        
        for path in targets:
            try:
                full_path = os.path.join(self.terminal.cwd, path)
                if os.path.isdir(full_path):
                    if recursive:
                        import shutil
                        shutil.rmtree(full_path)
                    else:
                        self.terminal.output_buffer.add(f"rm: cannot remove '{path}': Is a directory", TERM_CONFIG['error_color'])
                else:
                    os.remove(full_path)
            except Exception as e:
                if not force:
                    self.terminal.output_buffer.add(f"rm: cannot remove '{path}': {e}", TERM_CONFIG['error_color'])
    
    def cmd_cat(self, args):
        if not args:
            self.terminal.output_buffer.add("cat: missing file operand", TERM_CONFIG['error_color'])
            return
        for path in args:
            try:
                full_path = os.path.join(self.terminal.cwd, path)
                with open(full_path, 'r') as f:
                    self.terminal.output_buffer.add(f.read().rstrip())
            except Exception as e:
                self.terminal.output_buffer.add(f"cat: {path}: {e}", TERM_CONFIG['error_color'])
