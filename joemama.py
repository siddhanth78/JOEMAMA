import os
import sys
import termios
import tty
import subprocess
import shutil
from datetime import datetime
import tempfile

#TODO: error handling in tokenize_

cmdlist = ['new', 'newdir', 'list', 'copyto', 'moveto', 'meta', 'edit', 'runcmd', 'currpath', 'rename', 'clear', 'remove', 'help']
cmdlist.sort()

def check_dirs(query, paths):
    pathli = []
    for p in paths:
        if p.startswith(query):
            pathli.append(p)
    others = [x for x in paths if x not in pathli and query in x]
    pathli.extend(others)
    return pathli

def check_cmd(command, cmdlist):
    cmdli = []
    for c in cmdlist:
        if c.startswith(command):
            cmdli.append(c)
    others = [x for x in cmdlist if x not in cmdli and command in x]
    cmdli.extend(others)
    return cmdli

def clear_current_line():
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def display_cmdlist(cm, cmds, display):
    clear_current_line()
    size = os.get_terminal_size()
    cmlen = len(cm) + len(display) + 7
    if cmds:
        suggestions_str = ' | '.join(cmds)
        total = f"{display}{cm} [{suggestions_str[:size.columns-cmlen]+'...' if len(suggestions_str) > size.columns-cmlen else suggestions_str}]"
        sys.stdout.write(total)
    else:
        total = f"{display}{cm}"
        sys.stdout.write(total)
    sys.stdout.flush()

def display_pathlist(query, paths, currpath):
    clear_current_line()
    size = os.get_terminal_size()
    query = currpath + '/' + query if query else currpath
    query_curr = query.split('/')
    par, chi = query_curr[-2], query_curr[-1]
    parchilen = len(par) + len(chi) + 7
    if paths:
        suggestions_str = ' | '.join(paths)
        disp = f"{par}/{chi} [{suggestions_str[:size.columns-parchilen]+'...' if len(suggestions_str) > size.columns-parchilen else suggestions_str}]"
        sys.stdout.write(disp)
    else:
        disp = f"{par}/{chi}"
        sys.stdout.write(disp)
    sys.stdout.flush()
    return disp

def getdirs(root):
    pathlist = []
    try:
        paths = os.listdir(root)
        for path in paths:
            full_path = os.path.join(root, path)
            if os.path.isdir(full_path) or os.path.isfile(full_path):
                pathlist.append(path)
    except OSError as e:
        sys.stderr.write(f"Error accessing directory: {e}\n")
    return pathlist

def update_path(currpath):
    pathlist = getdirs(currpath)
    sys.stdout.write(currpath)
    sys.stdout.flush()
    return pathlist

def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

def run_script_in_new_terminal(command):
    tmppath = os.path.join(os.getcwd(), 'tmp/PIPEOUT.txt')
    try:
        script = f'''
    tell application "Terminal"
        set newTab to do script
        set theWindow to first window of (every window whose tabs contains newTab)

        do script "{command} | tee {tmppath}" in newTab
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
        print(f"Error running script: {e}")

    with open(tmppath, 'r') as f:
        pipeout = f.read()

    sys.stdout.write(''.join([p if p!= '\n' else '\n\r' for p in pipeout]) + '\n')
    sys.stdout.flush()
    

def tokenize_(tokens, currpath, cmdli):
    if tokens.strip() == '::help':
        with open('licoms.txt', 'r') as f:
            help = f.read()
        sys.stdout.write(''.join([h if h!= '\n' else '\n\r' for h in help]) + '\n')
        sys.stdout.flush()
        return
    if tokens.strip() == '::currpath':
        sys.stdout.write(currpath + '\n')
        sys.stdout.flush()
        return
    if tokens.strip() == '::clear':
        os.system('clear')
        return
    if tokens.strip() == '::list':
        sys.stdout.write('\n\r'.join(os.listdir(currpath)) + '\n\n')
        sys.stdout.flush()
        return
    
    tokenli = tokens.split("::")
    com = ''
    arg = ''
    flag = 1

    file_or_dir = tokenli[0].strip()
    cmdtokenli = tokenli[1].strip().split(">>")

    if cmdtokenli[0].strip() == 'runcmd':
        run_script_in_new_terminal(f'cd {currpath} && ' + cmdtokenli[1].strip())
        return
    
    if file_or_dir == '':
        sys.stdout.write("Missing file or dir name\n")
        sys.stdout.flush()
        return
    
    if len(cmdtokenli) == 1:
        com = cmdtokenli[0].strip()
        flag = 1
    elif len(cmdtokenli) >= 2:
        com, arg = cmdtokenli[0].strip(), cmdtokenli[1].strip()
        flag = 2
        if arg == '':
            sys.stdout.write("Missing command arg\n")
            sys.stdout.flush()
            return

    if com not in cmdli:
        sys.stdout.write(f"Invalid command: '{com}'\n")
        sys.stdout.flush()
        return
    
    out = ''
    fullpath = os.path.join(currpath, file_or_dir)
    if os.path.exists(fullpath) == False and com not in ['new', 'newdir']:
        sys.stdout.write("Path doesn't exist\n")
        sys.stdout.flush()
        return

    if flag == 2:
        if com == 'rename' or com == 'moveto':
            shutil.move(fullpath, arg)
        elif com == 'copyto':
            shutil.copy2(fullpath, arg)
        elif com == 'edit':
            try:
                subprocess.run(f"{arg} {fullpath}", shell=True, text=True)
            except subprocess.CalledProcessError as e:
                print("Failed to open file")
        else:
            sys.stdout.write("Command doesn't accept arg\n")
            sys.stdout.flush()
    
    elif flag == 1:
        if com == 'new':
            f = open(fullpath, 'x')
            f.close()
        elif com == 'newdir':
            os.mkdir(fullpath)
        elif com == 'list':
            out = '\n\r'.join(os.listdir(fullpath)) + '\n\n'
        elif com == 'meta':
            stats = os.stat(fullpath)
            out = f'''File name:     {file_or_dir}\r
Size (KB):     {sizeFormat(stats.st_size)}\r
Created:       {timeConvert(stats.st_ctime)}\r
Modified:      {timeConvert(stats.st_mtime)}\r
Last accessed: {timeConvert(stats.st_atime)}\r\n\n'''
        
        elif com == 'remove':
            if os.path.isfile(fullpath):
                os.remove(fullpath)
            elif os.path.isdir(fullpath):
                os.rmdir(fullpath)
            
        sys.stdout.write(out)
        sys.stdout.flush()

def timeConvert(atime):
  dt = atime
  newtime = datetime.fromtimestamp(dt)
  return newtime.date()
   
def sizeFormat(size):
    newform = format(size/1024, ".2f")
    return newform + " KB"
    

def get_input(pathlist, currpath):
    fd = sys.stdin.fileno()
    original_settings = termios.tcgetattr(fd)
    input_chars = []
    cmd_chars = []
    paths = []
    comli = []
    subcomli = []
    query = ''
    command = ''
    display = ''
    tokens = ''
    global cmdlist
    try:
        hide_cursor()
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)

            if char == '\n' or char == '\r':
                os.system("clear")
                #pathlist, currpath = tokenize_query(tokens, pathlist, currpath)
                if '::' in query:
                    if comli:
                        tokens = query + ''.join(list(comli[0]))
                    else:
                        tokens = query + command
                    tokenize_(tokens, currpath, cmdlist)
                elif query == "..":
                    currpath = os.path.dirname(currpath)
                else:
                    if paths:
                        tokens = ''.join(list(paths[0]))
                    else:
                        tokens = query

                    currpath = os.path.join(currpath, tokens)

                    if os.path.exists(currpath) == False:
                        sys.stdout.write(f"'{tokens}' deosn't exist\n")
                        sys.stdout.flush()
                        currpath = os.path.dirname(currpath)

                    if os.path.isfile(currpath):
                        try:
                            subprocess.run(f"open {currpath}", shell=True, text=True)
                        except subprocess.CalledProcessError as e:
                            print("Failed to open file")
                        currpath = os.path.dirname(currpath)

                pathlist = update_path(currpath)
                input_chars = []
                cmd_chars = []
                tokens = ''

            elif char == '\x7f' or char == '\b':
                if cmd_chars != []:
                    cmd_chars.pop()
                elif cmd_chars == [] and input_chars!= []:
                    input_chars.pop()
                elif cmd_chars == [] and input_chars== []:
                    pass
            
            elif char == '\t':
                if '::' in query:
                    if comli:
                        cmd_chars = list(comli[0])
                        comli = []
                else:
                    if paths:
                        input_chars = list(paths[0])
                        paths = []

            elif char == '\x1b':
                break

            else:
                if '::' in query:
                    cmd_chars.append(char)
                else:
                    input_chars.append(char)

            query = ''.join(input_chars)
            command = ''.join(cmd_chars)

            if '::' in query:
                display = display_pathlist(query, paths, currpath)
                comli = check_cmd(command, cmdlist)
                display_cmdlist(command, comli, display)
            else:
                paths = check_dirs(query, pathlist)
                display = display_pathlist(query, paths, currpath)


    finally:
        show_cursor()
        termios.tcsetattr(fd, termios.TCSADRAIN, original_settings)

def main():
    os.system('clear')
    currpath = os.path.expanduser("~")
    pathlist = update_path(currpath)
    paths = check_dirs('', pathlist)
    display_pathlist('', paths, currpath)
    get_input(pathlist, currpath)

if __name__ == '__main__':
    main()
