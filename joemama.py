import os
import sys
import termios
import tty
import subprocess
import shutil
from datetime import datetime

vars = {'$CURRDIR': os.path.expanduser('~'),
        }

pli = []
leaves = []

cmdlist = ['new', 'newdir', 'list', 'copyto', 'moveto', 'info', 'editor', 'runcmd',
           'currdir', 'rename', 'clear', 'remove', 'variable', 'quit', 'varlist', 'purge']
cmdlist.sort()

def read_history():
    history = []
    if os.path.exists('.history'):
        with open('.history', 'r') as file:
            history = file.readlines()
    return history

def help_():
    doc = '''

Just an Ordinary and Easy-to-use Mac OS file manager\r

Navigate files fast using partial searches with no additional text\r

Click `return` to go into a directory, open a file, or use a command\r

Clicking `return` on a partial search will select the first option in the suggestions\r

Clicking `tab` will autofill the partial search with the first option in the suggestions\r

Enter `..` to go back to the parent directory\r

Navigate through previous commands using `up arrow` and `down arrow`\r

Use `-> <dirname>` to jump to an existing directory anywhere inside the current directory\r
Variables can be used in place of directory names\r
Commands cannot be used while jumping\r

Access commands -> `::`\r

Command list:\r

clear\r
copyto\r
currdir\r
editor\r
info\r
list\r
moveto\r
new\r
newdir\r
purge\r
quit\r
remove\r
rename\r
runcmd\r
variable\r
varlist\r

clear - clear screen\r
Usage: `::clear`\r

copyto - copy contents of file or directory to new file or directory\r
Usage: `<filename>::copyto >> <destination>`\r

currdir - display path to current directory\r
Usage: `::currdir`\r

editor - open file or directory in preferred editor\r
Usage: `<filename>::editor >> <file editor>`\r

info - display file or directory information\r
Usage: `<filename>::info`\r

list - list all files and directories in directory\r
Usage: `<dirname>::list` or `::list`\r

moveto - move file or directory to existing directory\r
Usage: `<filename>::moveto >> <destination>`\r

new - create new file\r
Usage: `<filename>::new`\r

newdir - create new directory\r
Usage: `<dirname>::newdir`\r

purge - remove existing directory and its contents\r
Usage: `<dirname>::purge`\r

quit - quit the terminal\r
Usage: `::quit`\r

remove - remove existing file or directory\r
Usage: `<filename or dirname>::remove`\r

rename - rename existing file or directory\r
Usage: `<filename or dirname>::rename >> <newfilename or newdirname>`\r

runcmd - run custom bash command in new terminal\r
Usage: `::runcmd >> <bash command>`\r

Command runs in current directory by default\r
To run in a different directory use `cd <dirname> &&` before running the command\r
Example:\r
`::runcmd >> cd path/to/preferred/directory && <bash command>`\r

variable - create and set variable with custom value\r
Usage: `::variable >> <varname> >> <value>`\r

To access variables anywhere in the query, use `$<varname>`\r
Example:\r
```\r
::variable >> newfilename >> new.txt\r
old.txt::rename >> $newfilename\r
```\r

Variables can only be used in command arguments\r

'CURRDIR' is a default variable with its value being the current directory\r
It can be accessed anytime with `$CURRDIR`\r
User defined variables get cleared after every session\r

varlist - list all variables\r
Usage: `::varlist`\r

'''
    sys.stdout.write(doc)
    sys.stdout.flush()

def get_leaf(x):
    return x.split('/')[-1]

def update_leaves():
    global pli, leaves
    dirli = set(list(map(get_leaf, pli)))
    leaves = list(dirli)
    leaves.sort()

def check_all_dirs(query, paths):
    pathli = []
    for p in paths:
        if p.startswith(query):
            pathli.append(p)
    others = [x for x in paths if x not in pathli and query in x]
    pathli.sort()
    pathli.extend(others)
    return pathli

def check_dirs(query, paths):
    pathli = []
    for p in paths:
        if p.startswith(query):
            pathli.append(p)
    others = [x for x in paths if x not in pathli and query in x]
    pathli.sort()
    pathli.extend(others)
    return pathli

def check_cmd(command, cmdlist):
    cmdli = []
    for c in cmdlist:
        if c.startswith(command):
            cmdli.append(c)
    others = [x for x in cmdlist if x not in cmdli and command in x]
    cmdli.sort()
    cmdli.extend(others)
    return cmdli

def clear_current_line():
    sys.stdout.write('\0338\033[0J')
    sys.stdout.flush()

def display_cmdlist(cm, cmds, display):
    clear_current_line()
    size = os.get_terminal_size()
    cmlen = len(cm) + len(display) + 7
    if cmds:
        suggestions_str = ' | '.join(cmds[:10])
        total = f"{display}{cm} [{suggestions_str}]"
    else:
        total = f"{display}{cm}"
    sys.stdout.write(total)
    sys.stdout.flush()

def display_varlist(v_, vli_, display):
    clear_current_line()
    size = os.get_terminal_size()
    vlen = len(v_) + len(display) + 7
    if vli_:
        suggestions_str = ' | '.join(vli_[:10])
        total = f"{display}{v_} [{suggestions_str}]"
    else:
        total = f"{display}{v_}"
    sys.stdout.write(total)
    sys.stdout.flush()

def display_pathlist(query, paths, currpath):
    clear_current_line()
    size = os.get_terminal_size()
    query = currpath + '%||%' + query if query else currpath + '%||%'
    query_curr = query.split('%||%')
    par, chi = query_curr[-2], query_curr[-1]
    parli = par.split('/')
    par = parli[-2].strip() + '/' + parli[-1].strip()
    parchilen = len(par) + len(chi) + 7
    if paths:
        suggestions_str = ' | '.join(paths[:10])
        disp = f"{par}/{chi} [{suggestions_str}]"
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
        sys.stderr.write(f"Error accessing directory: {e}\n\r")
        pathlist = ["ERROR%"]
    return pathlist

def get_all_dirs(root_dir):
    directories = []
    if os.access(root_dir, os.R_OK):
        try:
            for entry in os.scandir(root_dir):
                if entry.is_dir(follow_symlinks=False):
                    directories.append(entry.path)
                    directories.extend(get_all_dirs(entry.path))  # Recursively add subdirectories
        except PermissionError:
            pass
        except Exception as e:
            pass
    else:
        pass
    return directories

def update_path(currpath):
    global vars
    pathlist = getdirs(currpath)
    vars['$CURRDIR'] = currpath
    return pathlist

def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

def run_script_in_new_terminal(command):
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
        print(f"Error running script: {e}")

    with open(tmppath, 'r') as f:
        pipeout = f.read()

    os.remove(tmppath)

    sys.stdout.write('\n'+''.join([p if p!= '\n' else '\n\r' for p in pipeout]) + '\n\r')
    sys.stdout.flush()

def save_vars(key, val):
    global vars
    vars['$'+key] = val
    

def tokenize_(tokens, currpath, cmdli):
    global vars, pli
    if '::$' in tokens.strip() or tokens[0].strip() == '$':
        sys.stdout.write("Variables can only be used in command arguments\n\r")
        sys.stdout.flush()
        return
    if tokens.strip() == '::quit':
        sys.exit(0)
    if tokens.strip() == '::varlist':
        sys.stdout.write(f"Use variable with `$<varname>`\n\n\r")
        for i, j in vars.items():
            i = i.strip('$')
            sys.stdout.write(f"{i} = {j}\n\r")
            sys.stdout.flush()
        sys.stdout.write("\n")
        sys.stdout.flush()
        return
    if tokens.strip() == '::currdir':
        sys.stdout.write(currpath + '\n\r')
        sys.stdout.flush()
        return
    if tokens.strip() == '::clear':
        os.system('clear')
        return
    if tokens.strip() == '::list':
        sys.stdout.write('\n\r'.join(os.listdir(currpath)) + '\n\n\r')
        sys.stdout.flush()
        return
    
    tokenli = tokens.split("::")
    com = ''
    arg = ''
    flag = 1

    file_or_dir = tokenli[0].strip()

    try:
        cmdtokenli = tokenli[1].strip().split(">>")
    except:
        sys.stdout.write("Invalid command\n\r")
        sys.stdout.flush()
        return
    
    if cmdtokenli[0].strip() == 'variable':
        if len(cmdtokenli) < 3:
            sys.stdout.write("Missing command args\n\r")
            sys.stdout.flush()
            return
        if '$' in cmdtokenli[1].strip():
            sys.stdout.write("Cannot use '$' in variable name\n\r")
            sys.stdout.flush()
            return
        save_vars(cmdtokenli[1].strip(), cmdtokenli[2].strip())
        return
    
    if len(cmdtokenli) > 1:
        for i, j in vars.items():
                cmdtokenli[1] = cmdtokenli[1].replace(i, j)

    if cmdtokenli[0].strip() == 'runcmd':
        if len(cmdtokenli) < 2:
            sys.stdout.write("Missing command arg\n\r")
            sys.stdout.flush()
            return
        run_script_in_new_terminal(f'cd {currpath} && ' + cmdtokenli[1].strip())
        return
    
    if file_or_dir == '':
        sys.stdout.write("Missing file or dir name\n\r")
        sys.stdout.flush()
        return
    
    if len(cmdtokenli) == 1:
        com = cmdtokenli[0].strip()
        flag = 1
    elif len(cmdtokenli) >= 2:
        com, arg = cmdtokenli[0].strip(), cmdtokenli[1].strip()
        flag = 2
        if arg == '':
            sys.stdout.write("Missing command arg\n\r")
            sys.stdout.flush()
            return

    if com not in cmdli:
        sys.stdout.write(f"Invalid command: '{com}'\n\r")
        sys.stdout.flush()
        return
    
    out = ''
    fullpath = os.path.join(currpath, file_or_dir)
    if os.path.exists(fullpath) == False and com not in ['new', 'newdir']:
        sys.stdout.write("Path doesn't exist\n\r")
        sys.stdout.flush()
        return

    argpath = os.path.join(currpath, arg)
    if os.path.exists(argpath) == False and com not in ['rename', 'editor', 'copyto'] and flag == 2:
        sys.stdout.write("Path doesn't exist\n\r")
        sys.stdout.flush()
        return

    if flag == 2:
        if com == 'rename' or com == 'moveto':
            try:
                dircheck = os.path.isdir(fullpath)
                shutil.move(fullpath, argpath)
                if dircheck:
                    lip = get_all_dirs(argpath)
                    pli.remove(fullpath)
                    for i in lip:
                        pli.append(i)
            except IOError as err:
                print(f"Couldn't move file: {err}")
        elif com == 'copyto':
            try:
                if os.path.isfile(fullpath):
                    shutil.copy2(fullpath, argpath)
                elif os.path.isdir(fullpath):
                    shutil.copytree(fullpath, argpath)
                    lip = get_all_dirs(argpath)
                    for i in lip:
                        pli.append(i)
            except IOError as err:
                print(f"Couldn't move file: {err}")
        elif com == 'editor':
            try:
                subprocess.run(f"{arg} {fullpath}", shell=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to open file: {e}")
        else:
            sys.stdout.write("Command doesn't accept arg\n\r")
            sys.stdout.flush()
    
    elif flag == 1:
        if com == 'new':
            try:
                with open(fullpath, "x") as f:
                    f.close()
            except IOError as e:
                print(f"Couldn't create file: {e}")
        elif com == 'newdir':
            try:
                os.mkdir(fullpath)
                pli.append(fullpath)
                update_leaves()
            except IOError as e:
                print(f"Couldn't create directory: {e}")
        elif com == 'list':
            out = '\n\r'.join(os.listdir(fullpath)) + '\n\n\r'
        elif com == 'info':
            stats = os.stat(fullpath)
            out = f'''Name:     {file_or_dir}\r
Size (KB):     {sizeFormat(stats.st_size)}\r
Created:       {timeConvert(stats.st_ctime)}\r
Modified:      {timeConvert(stats.st_mtime)}\r
Last accessed: {timeConvert(stats.st_atime)}\r\n\n\r'''
        
        elif com == 'remove':
            try:
                if os.path.isfile(fullpath):
                    os.remove(fullpath)
                elif os.path.isdir(fullpath):
                    os.rmdir(fullpath)
                    pli.remove(fullpath)
                    update_leaves()
            except IOError as e:
                print(f"Couldn't remove file or dir: {e}")
        elif com == 'purge':
            try:
                lip = get_all_dirs(fullpath)
                shutil.rmtree(fullpath)
                pli.remove(fullpath)
                for i in lip:
                    pli.remove(i)
                update_leaves()
            except IOError as e:
                print(f"Couldn't purge dir: {e}")
        else:
            sys.stdout.write("Missing command arg(s)\n\r")
            sys.stdout.flush()

            
        sys.stdout.write(out)
        sys.stdout.flush()

def timeConvert(atime):
  dt = atime
  newtime = datetime.fromtimestamp(dt)
  return newtime.date()
   
def sizeFormat(size):
    newform = format(size/1024, ".2f")
    return newform + " KB"

def check_vars(va, vlist):
    vli = []
    for v in vlist:
        if v.startswith(va):
            vli.append(v)
    others = [x for x in vlist if x not in vli and va in x]
    vli.sort()
    vli.extend(others)
    return vli

def check_var_in(query, command):
    global vars
    tokens = query+command
    ili = list(query)
    cli = list(command)
    tokenli = tokens.split(' ')
    subtoken = ''

    if '$' in tokenli[-1]:
        subtoken = tokenli[-1]

    if subtoken == '':
        return '', [], False, query, command, ili, cli
    
    subtokenli = subtoken.split('$')

    if len(subtokenli) < 2:
        return '', [], False, query, command, ili, cli
    
    varcheck = subtokenli[-1]

    for vk in vars.keys():
        if '$'+varcheck in vk:
            tokens = tokens[:-len('$'+varcheck)]
            token_split = tokens.split('::')
            if len(token_split) < 2:
                query = token_split[0]
                command = ''
                ili = list(query)
                cli = []
            elif len(token_split) >= 2:
                query = token_split[0]+'::'
                command = token_split[1]
                ili = list(query)
                cli = list(command)
            return '$'+varcheck, list('$'+varcheck), True, query, command, ili, cli
    return '', [], False, query, command, ili, cli
    

def get_input(pathlist, currpath):
    fd = sys.stdin.fileno()
    original_settings = termios.tcgetattr(fd)
    input_chars = []
    cmd_chars = []
    paths = []
    comli = []
    query = ''
    command = ''
    display = ''
    tokens = ''
    v = ''
    history = read_history()
    history_index = len(history)
    global cmdlist, vars, pli, leaves
    var_in = False
    varli = []
    vli = []
    try:
        hide_cursor()
        tty.setraw(fd)
        while True:
            char = sys.stdin.read(1)

            if char == '\n' or char == '\r':
                sys.stdout.write('\n\r')
                if query == '--help':
                    help_()
                    tokens = '--help'
                elif query.strip().startswith('->'):
                    if paths:
                        tokens = ''.join(list(paths[0]))
                    else:
                        tokens = query.split('->')[1]
                    tokens = tokens.strip()
                    if vli != []:
                        tokens = tokens + ''.join(list(vli[0]))
                    for i, j in vars.items():
                        tokens = tokens.replace(i, j)
                    matchli = []
                    for i in pli:
                        dirname = i.split('/')[-1]
                        if tokens == dirname:
                            matchli.append(i)
                    if len(matchli) == 1:
                        currpath = matchli[0]
                    elif len(matchli) < 1:
                        sys.stdout.write(f"Either '{tokens}' doesn't exist or scan/read permission is denied\n\r")
                        sys.stdout.write("If directory does exist and is accessible, navigate to it\n\r")
                        sys.stdout.flush()
                    elif len(matchli) > 1:
                        sys.stdout.write(f"{len(matchli)} matches found. Go to parent directory to ensure proper jump\n\r")
                        sys.stdout.flush()
                    tokens = '->'+tokens
                elif '::' in query:
                    if vli != []:
                        tokens = query + command + ''.join(list(vli[0]))
                        vli = []
                    elif comli:
                        tokens = query + ''.join(list(comli[0]))
                    else:
                        tokens = query + command
                    tokenize_(tokens, currpath, cmdlist)
                elif query == "..":
                    currpath = os.path.dirname(currpath)
                    tokens = '..'
                else:
                    query = query + ''.join(varli)
                    paths = check_dirs(query, pathlist)
                    if paths:
                        tokens = ''.join(list(paths[0]))
                    else:
                        tokens = query

                    try:
                        currpath = os.path.join(currpath, tokens)
                    except OSError as e:
                        sys.stdout.write(f"{e}\n\r")
                        sys.stdout.flush()
                        currpath = os.path.dirname(currpath)

                    if os.path.exists(currpath) == False:
                        sys.stdout.write(f"'{tokens}' doesn't exist\n\r")
                        sys.stdout.flush()
                        currpath = os.path.dirname(currpath)

                    if os.path.isfile(currpath):
                        try:
                            subprocess.run(f"open {currpath}", shell=True, text=True)
                        except subprocess.CalledProcessError as e:
                            sys.stdout.write(f"Failed to open file: {e}\n\r")
                            sys.stdout.flush()
                        currpath = os.path.dirname(currpath)

                with open('.history', 'a') as file:
                    file.write(tokens.strip()+'\n')

                pathlist = update_path(currpath)
                if pathlist == ["ERROR%"]:
                    currpath = os.path.dirname(currpath)
                    pathlist = update_path(currpath)
                input_chars = []
                cmd_chars = []
                varli = []
                vli = []
                tokens = ''
                history = read_history()
                history_index = len(history)
                query = ''
                paths = []
                
                sys.stdout.write('\r\0337')
                sys.stdout.flush()
                display = display_pathlist(query, paths, currpath)
                sys.stdout.write('\r\0337')
                sys.stdout.flush()

                continue

            elif char == '\x7f' or char == '\b':
                if varli != []:
                    varli.pop()
                elif cmd_chars != []:
                    cmd_chars.pop()
                elif cmd_chars == [] and input_chars!= []:
                    input_chars.pop()
                elif cmd_chars == [] and input_chars== []:
                    pass
            
            elif char == '\t':
                if var_in == True:
                    if vli:
                        varli = list(vli[0])
                        vli = []
                elif '::' in query:
                    if comli:
                        cmd_chars = list(comli[0])
                        comli = []
                else:
                    if paths:
                        if query.strip().startswith('->'):
                            input_chars = list('->'+paths[0])
                        else:
                            input_chars = list(paths[0])
                        paths = []

            elif char == '\x1b':
                next1, next2 = sys.stdin.read(1), sys.stdin.read(1)
                if next1 == '[':
                    if next2 == 'A':  # Up arrow
                        if history_index > 0:
                            history_index -= 1
                            query = history[history_index].strip('\n')
                            command = ''
                            if '::' in query:
                                queryli = query.split('::')
                                query = queryli[0].strip()+ '::'
                                command = queryli[1].strip()
                            input_chars = list(query)
                            cmd_chars = list(command)
                        elif history_index <= 0:
                            history_index = -1
                            query = ''
                            input_chars = []
                            cmd_chars = []
                    elif next2 == 'B':  # Down arrow
                        if history_index < len(history) - 1:
                            history_index += 1
                            query = history[history_index].strip('\n')
                            command = ''
                            if '::' in query:
                                queryli = query.split('::')
                                query = queryli[0].strip() + '::'
                                command = queryli[1].strip()
                            input_chars = list(query)
                            cmd_chars = list(command)
                        elif history_index >= len(history) - 1:
                            history_index = len(history)
                            query = ''
                            input_chars = []
                            cmd_chars = []

                    if '::' in query and query.strip().startswith('->')==False:
                        if command.strip() == '':
                            comli = []
                        else:
                            comli = check_cmd(command, cmdlist)

                        display = display_pathlist(query, [], currpath)
                        display_cmdlist(command, comli, display)
                    else:
                        if query.strip() == '':
                            paths = []
                        elif query.strip().startswith('->'):
                            if query.strip() == '->':
                                paths = []
                            else:
                                paths = check_all_dirs(query[2:], leaves)
                        else:
                            paths = check_dirs(query, pathlist)
                        display = display_pathlist(query, paths, currpath)

                    continue
                else:
                    continue

            elif char == '$':
                varli.append(char)
                var_in = True

            else:
                if var_in  == True:
                    varli.append(char)
                elif var_in == False:
                    if '::' in query:
                        cmd_chars.append(char)
                    else:
                        input_chars.append(char)

            if query.strip().startswith('->'):
                cmd_chars = []

            query = ''.join(input_chars)
            command = ''.join(cmd_chars)
            v = ''.join(varli)

            if var_in == False:
                v, varli, var_in, query, command, input_chars, cmd_chars = check_var_in(query, command)

            if var_in == True:
                qq = currpath + '%||%' + query + command if query or command else currpath + '%||%'
                qq_curr = qq.split('%||%')
                par, chi = qq_curr[-2], qq_curr[-1]
                parli = par.split('/')
                par = parli[-2].strip() + '/' + parli[-1].strip()
                display = f'{par}/{chi}'
                vli = check_vars(v, vars.keys())
                display_varlist(v, vli, display)
                if not vli or v.strip() == '':
                    if '::' in query:
                        cmd_chars.extend(list(v))
                    else:
                        input_chars.extend(list(v))
                    var_in = False
                    varli = []
                    vli = []
                    v = ''
                    query = ''.join(input_chars)
                    command = ''.join(cmd_chars)

            if var_in == False:
                if '::' in query and query.strip().startswith('->')==False:
                    if command.strip() == '':
                        comli = []
                    else:
                        comli = check_cmd(command, cmdlist)

                    display = display_pathlist(query, [], currpath)
                    display_cmdlist(command, comli, display)
                else:
                    if query.strip() == '':
                        paths = []
                    elif query.strip().startswith('->'):
                        if query.strip() == '->':
                            paths = []
                        else:
                            paths = check_all_dirs(query[2:], leaves)
                    else:
                        paths = check_dirs(query, pathlist)
                    display = display_pathlist(query, paths, currpath)


    finally:
        show_cursor()
        termios.tcsetattr(fd, termios.TCSADRAIN, original_settings)

def main():
    global pli
    os.system('clear')
    print("JOEMAMA 2.5")
    print("Use `--help` for more information\n")
    currpath = os.path.expanduser("~")
    pli = get_all_dirs(currpath)
    pli.append(os.path.expanduser("~"))
    update_leaves()
    pathlist = update_path(currpath)
    sys.stdout.write('\0337')
    sys.stdout.flush()
    sys.stdout.write(currpath.strip('/'))
    get_input(pathlist, currpath)

if __name__ == '__main__':
    main()
