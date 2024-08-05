import os
import tkinter as tk
from tkinter import ttk
import subprocess
import shutil
from datetime import datetime

class SimpleFileManagerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("JOEMAMA 1.4")
        self.master.geometry("600x450")

        self.default_editor = 'open'

        self.current_path = os.path.expanduser("~")
        self.vars = {'$CURRDIR': self.current_path}
        self.cmdlist = ['new', 'newdir', 'list', 'copyto', 'moveto', 'info', 'editor', 'runcmd',
                        'currdir', 'rename', 'remove', 'variable']
        self.cmdlist.sort()

        self.command_history = []  # Initialize the command_history here
        self.history_max_size = 20

        self.create_widgets()

    def create_widgets(self):
        # Frame for query entry and execute button
        self.query_frame = ttk.Frame(self.master)
        self.query_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Query Entry
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(self.query_frame, textvariable=self.query_var, width=50)
        self.query_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.query_entry.bind('<KeyRelease>', self.on_query_change)
        self.query_entry.bind('<Tab>', self.on_tab)
        self.query_entry.bind('<Return>', self.execute_command)

        # Execute Button
        self.execute_button = ttk.Button(self.query_frame, text="Execute", command=self.execute_command)
        self.execute_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Frame for history and variable dropdowns
        self.dropdown_frame = ttk.Frame(self.master)
        self.dropdown_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # History Label and Dropdown
        ttk.Label(self.dropdown_frame, text="History:").pack(side=tk.LEFT, padx=(0, 5))
        self.history_var = tk.StringVar()
        self.history_dropdown = ttk.Combobox(self.dropdown_frame, textvariable=self.history_var, width=25, state="readonly")
        self.history_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        self.history_dropdown.bind('<<ComboboxSelected>>', self.on_history_select)

        # Variable Label and Dropdown
        ttk.Label(self.dropdown_frame, text="Variables:").pack(side=tk.LEFT, padx=(0, 5))
        self.variable_var = tk.StringVar()
        self.variable_dropdown = ttk.Combobox(self.dropdown_frame, textvariable=self.variable_var, width=25, state="readonly")
        self.variable_dropdown.pack(side=tk.LEFT)
        self.variable_dropdown.bind('<<ComboboxSelected>>', self.on_variable_select)

        # Suggestions Listbox
        self.suggestions_listbox = tk.Listbox(self.master, height=5, width=70)
        self.suggestions_listbox.pack(padx=10, pady=(0, 10), fill=tk.X)
        self.suggestions_listbox.bind('<<ListboxSelect>>', self.on_suggestion_select)

        # Current Directory Label
        self.current_dir_var = tk.StringVar(value=f"{self.current_path}")
        self.current_dir_label = ttk.Label(self.master, textvariable=self.current_dir_var, anchor='w')
        self.current_dir_label.pack(padx=10, pady=(0, 5), fill=tk.X)

        # Output Text
        self.output_text = tk.Text(self.master, height=10, width=70, wrap=tk.WORD)
        self.output_text.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, 'Enter --help for more information')

        # Initialize dropdowns
        self.update_history_dropdown()
        self.update_variable_dropdown()

    def show_help(self):
        help_text = """
JOEMAMA 1.4 - Just an Ordinary and Easy-to-use Mac OS file manager

Navigate files fast using partial searches with no additional text
Click `return` to go into a directory, open a file, or use a command
Clicking `tab` will autofill the partial search with the first option in the suggestions
Enter `..` to go back to the parent directory
Navigate through previous commands using the history dropdown

Commands:
    <filename>::copyto       Copy file to existing file or directory
                Usage: <filename>::copyto >> <destination>
    ::currdir                Display path to current directory
    <filename>::editor       Open file or directory in preferred editor
                Usage: <filename>::editor >> <file editor>
    <filename>::info         Display file or directory information
    <dirname>::list          List all files and directories in directory
                Usage: <dirname>::list or ::list for current directory
    <filename>::moveto       Move file to existing directory
                Usage: <filename>::moveto >> <destination>
    <filename>::new          Create new file
    <dirname>::newdir        Create new directory
    <filename>::remove       Remove existing file or directory
    <filename>::rename       Rename existing file or directory
                Usage: <filename>::rename >> <newfilename>
    ::runcmd                 Run custom bash command in new terminal
                Usage: ::runcmd >> <bash command>
    ::variable               Create and set variable with custom value
                Usage: ::variable >> <varname> >> <value>

Variables:
    To access variables anywhere in the query, use $<varname>
    Use the variable dropdown to autofill existing variables
    'CURRDIR' is a default variable with its value being the current directory
    It can be accessed anytime with $CURRDIR
    """
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, help_text)

    def on_history_select(self, event):
        selected_command = self.history_var.get()
        self.query_var.set(selected_command)
        self.history_dropdown.set('')  # Clear the selection in the dropdown

    def add_to_history(self, command):
        if command and command not in self.command_history:
            self.command_history.insert(0, command)
            if len(self.command_history) > self.history_max_size:
                self.command_history.pop()
            self.update_history_dropdown()

    def update_history_dropdown(self):
        self.history_dropdown['values'] = self.command_history

    def on_query_change(self, event):
        query = self.query_var.get()
        self.suggestions_listbox.delete(0, tk.END)
        if '::' in query:
            cmd = query.split('::')[1]
            suggestions = [c for c in self.cmdlist if c.startswith(cmd)]
        else:
            suggestions = self.get_path_suggestions(query)
        for suggestion in suggestions:
            self.suggestions_listbox.insert(tk.END, suggestion)

    def get_path_suggestions(self, query):
        full_path = os.path.join(self.current_path, query)
        dir_path = os.path.dirname(full_path)
        prefix = os.path.basename(full_path)
        try:
            return [f for f in os.listdir(dir_path) 
                    if f.startswith(prefix) and f != '.DS_Store']
        except OSError:
            return []

    def on_suggestion_select(self, event):
        if self.suggestions_listbox.curselection():
            selected = self.suggestions_listbox.get(self.suggestions_listbox.curselection())
            self.apply_suggestion(selected)

    def apply_suggestion(self, selected):
        current_query = self.query_var.get()
        if '::' in current_query:
            base, _ = current_query.split('::', 1)
            self.query_var.set(f"{base}::{selected}")
        else:
            self.query_var.set(os.path.join(os.path.dirname(current_query), selected))
        self.query_entry.icursor(tk.END)  # Move cursor to the end
        self.query_entry.xview_moveto(1)  # Scroll to the end if needed

    def on_tab(self, event):
        if self.suggestions_listbox.size() > 0:
            first_suggestion = self.suggestions_listbox.get(0)
            self.apply_suggestion(first_suggestion)
        return 'break'  # Prevents default Tab behavior

    def execute_command(self, event=None):
        query = self.query_var.get()
        self.output_text.delete('1.0', tk.END)
        if query == '--help':
            self.show_help()
        elif query == '..':
            self.go_to_parent_directory()
        elif '::' in query:
            self.handle_command(self.replace_variables(query))
        else:
            self.navigate_path(self.replace_variables(query))
        self.add_to_history(query)
        self.query_var.set('')
        self.query_entry.focus_set()  # Set focus back to entry after execution
        self.get_path_suggestions(query)


    def replace_variables(self, query):
        for var, value in self.vars.items():
            query = query.replace(var, value)
        return query

    def go_to_parent_directory(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir != self.current_path:  # Check if we're not at the root
            self.current_path = parent_dir
            self.vars['$CURRDIR'] = self.current_path
            self.current_dir_var.set(f"{self.current_path}")
            self.output_text.insert(tk.END, f"Changed directory to: {self.current_path}\n")
        else:
            self.output_text.insert(tk.END, "Already at the root directory.\n")

    def handle_command(self, query):
        parts = query.split('::')
        if len(parts) != 2:
            self.output_text.insert(tk.END, "Invalid command format\n")
            return
        
        file_or_dir, command = parts
        file_or_dir = file_or_dir.strip()
        command = command.strip()

        if command == 'list':
            self.list_directory(file_or_dir)
        elif command == 'info':
            self.show_info(file_or_dir)
        elif command == 'new':
            self.create_file(file_or_dir)
        elif command == 'newdir':
            self.create_directory(file_or_dir)
        elif command == 'remove':
            self.remove_item(file_or_dir)
        elif command == 'currdir':
            self.output_text.insert(tk.END, self.current_path + '\n')
        elif command.startswith('copyto'):
            self.copy_item(file_or_dir, command)
        elif command.startswith('moveto'):
            self.move_item(file_or_dir, command)
        elif command.startswith('runcmd'):
            self.run_command(command)
        elif command.startswith('variable'):
            self.set_variable(command)
        elif command.startswith('editor'):
            self.open_in_editor(file_or_dir, command)
        elif command.startswith('rename'):
            self.rename_item(file_or_dir, command)
        else:
            self.output_text.insert(tk.END, f"Command '{command}' not implemented\n")

    def open_in_editor(self, file_path, command):
        parts = command.split('>>')
        editor = self.default_editor

        if len(parts) > 1:
            editor = parts[1].strip()

        full_path = os.path.join(self.current_path, file_path)

        if not os.path.exists(full_path):
            self.output_text.insert(tk.END, f"File does not exist: {full_path}\n")
            return

        try:
            if editor == 'open':
                # For macOS, use 'open' command
                subprocess.run(['open', full_path])
            else:
                # For other editors, run the specified command
                subprocess.run([editor, full_path])
            self.output_text.insert(tk.END, f"Opened {full_path} with {editor}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error opening file: {str(e)}\n")

    def rename_item(self, old_name, command):
        parts = command.split('>>')
        if len(parts) != 2:
            self.output_text.insert(tk.END, "Invalid rename command format. Use 'rename >> new_name'\n")
            return

        new_name = parts[1].strip()
        old_path = os.path.join(self.current_path, old_name)
        new_path = os.path.join(self.current_path, new_name)

        if not os.path.exists(old_path):
            self.output_text.insert(tk.END, f"File or directory does not exist: {old_path}\n")
            return

        if os.path.exists(new_path):
            self.output_text.insert(tk.END, f"A file or directory already exists with the name: {new_name}\n")
            return

        try:
            os.rename(old_path, new_path)
            self.output_text.insert(tk.END, f"Successfully renamed '{old_name}' to '{new_name}'\n")
        except OSError as e:
            self.output_text.insert(tk.END, f"Error renaming: {str(e)}\n")

    def set_variable(self, command):
        parts = command.split('>>')
        if len(parts) != 3:
            self.output_text.insert(tk.END, "Invalid variable command format. Use 'variable >> <varname> >> <value>'\n")
            return

        _, varname, value = [part.strip() for part in parts]
        if not varname.startswith('$'):
            varname = '$' + varname

        self.vars[varname] = value
        self.output_text.insert(tk.END, f"Variable {varname} set to: {value}\n")
        self.update_variable_dropdown()

    def on_variable_select(self, event):
        selected_variable = self.variable_var.get()
        if selected_variable:
            var_name, var_value = selected_variable.split(' = ')
            self.query_var.set(self.query_var.get() + var_name)
        self.variable_dropdown.set('')  # Clear the selection in the dropdown

    def update_variable_dropdown(self):
        var_list = [f"{var} = {value}" for var, value in self.vars.items()]
        self.variable_dropdown['values'] = var_list

    def run_command(self, command):
        parts = command.split('>>')
        if len(parts) != 2:
            self.output_text.insert(tk.END, "Invalid runcmd format. Use 'runcmd >> <bash command>'\n")
            return

        bash_command = parts[1].strip()
        full_command = f"cd {self.current_path} && {bash_command}"
        
        try:
            output = self.run_script_in_new_terminal(full_command)
            self.output_text.insert(tk.END, output)
        except Exception as e:
            self.output_text.insert(tk.END, f"Error executing command: {str(e)}\n")

    def run_script_in_new_terminal(self, command):
        tmppath = os.path.join(os.getcwd(), 'PIPEOUT.txt')
        f = open(tmppath, 'a')
        f.close()
        try:
            script = f'''
            tell application "Terminal"
                set newTab to do script
                set theWindow to first window of (every window whose tabs contains newTab)

                do script "{command} |& tee -a {tmppath}" in newTab
                repeat
                    delay 0.05
                    if not busy of newTab then exit repeat
                end repeat

                repeat with i from 1 to the count of theWindow's tabs
                    if item i of theWindow's tabs is newTab then close theWindow
                end repeat
            end tell'''
            proc = subprocess.Popen(['osascript', '-e', script], text=True)
            proc.wait()
        except subprocess.CalledProcessError as e:
            return f"Error running script: {e}\n"

        with open(tmppath, 'r') as f:
            pipeout = f.read()

        os.remove(tmppath)

        return ''.join([p if p != '\n' else '\n\r' for p in pipeout]) + '\n'

    def navigate_path(self, path):
        full_path = os.path.join(self.current_path, path)
        if os.path.isdir(full_path):
            self.current_path = full_path
            self.vars['$CURRDIR'] = self.current_path
            self.current_dir_var.set(f"{self.current_path}")
            self.output_text.insert(tk.END, f"Changed directory to: {self.current_path}\n")
        elif os.path.isfile(full_path):
            self.output_text.insert(tk.END, f"Opening file: {full_path}\n")
            self.open_file(full_path)
        else:
            self.output_text.insert(tk.END, f"Path does not exist: {full_path}\n")

    def list_directory(self, path):
        full_path = os.path.join(self.current_path, path)
        try:
            items = os.listdir(full_path)
            for item in items:
                self.output_text.insert(tk.END, item + '\n')
        except OSError as e:
            self.output_text.insert(tk.END, f"Error listing directory: {e}\n")

    def show_info(self, path):
        full_path = os.path.join(self.current_path, path)
        try:
            stats = os.stat(full_path)
            info = f"Name: {os.path.basename(full_path)}\n"
            info += f"Size: {self.format_size(stats.st_size)}\n"
            info += f"Created: {datetime.fromtimestamp(stats.st_ctime)}\n"
            info += f"Modified: {datetime.fromtimestamp(stats.st_mtime)}\n"
            info += f"Accessed: {datetime.fromtimestamp(stats.st_atime)}\n"
            self.output_text.insert(tk.END, info)
        except OSError as e:
            self.output_text.insert(tk.END, f"Error getting info: {e}\n")

    def create_file(self, filename):
        full_path = os.path.join(self.current_path, filename)
        try:
            with open(full_path, 'w') as f:
                pass
            self.output_text.insert(tk.END, f"Created file: {full_path}\n")
        except OSError as e:
            self.output_text.insert(tk.END, f"Error creating file: {e}\n")

    def create_directory(self, dirname):
        full_path = os.path.join(self.current_path, dirname)
        try:
            os.mkdir(full_path)
            self.output_text.insert(tk.END, f"Created directory: {full_path}\n")
        except OSError as e:
            self.output_text.insert(tk.END, f"Error creating directory: {e}\n")

    def remove_item(self, path):
        full_path = os.path.join(self.current_path, path)
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                os.rmdir(full_path)
            self.output_text.insert(tk.END, f"Removed: {full_path}\n")
        except OSError as e:
            self.output_text.insert(tk.END, f"Error removing item: {e}\n")

    def open_file(self, path):
        try:
            os.startfile(path)
        except AttributeError:
            subprocess.call(['open', path])
        except Exception as e:
            self.output_text.insert(tk.END, f"Error opening file: {e}\n")

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    def copy_item(self, source, command):
        parts = command.split('>>')
        if len(parts) != 2:
            self.output_text.insert(tk.END, "Invalid copyto command format\n")
            return
        
        destination = parts[1].strip()
        source_path = os.path.join(self.current_path, source)
        dest_path = os.path.join(self.current_path, destination)

        try:
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            self.output_text.insert(tk.END, f"Copied {source_path} to {dest_path}\n")
        except OSError as e:
            self.output_text.insert(tk.END, f"Error copying: {e}\n")

    def move_item(self, source, command):
        parts = command.split('>>')
        if len(parts) != 2:
            self.output_text.insert(tk.END, "Invalid moveto command format\n")
            return
        
        destination = parts[1].strip()
        source_path = os.path.join(self.current_path, source)
        dest_path = os.path.join(self.current_path, destination)

        try:
            shutil.move(source_path, dest_path)
            self.output_text.insert(tk.END, f"Moved {source_path} to {dest_path}\n")
        except OSError as e:
            self.output_text.insert(tk.END, f"Error moving: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleFileManagerGUI(root)
    root.mainloop()
