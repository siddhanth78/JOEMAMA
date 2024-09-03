- <ins>J</ins>ust an <ins>O</ins>rdinary and <ins>E</ins>asy-to-use <ins>MA</ins>c OS file <ins>MA</ins>nager
- Requires Python 3

## Current versions:
- Mac OS: JOEMAMA 2.6
- Windows: JOEMAMA-WIN 2.5 (Bugged)
- GUI: JOEMAMA 1.4
  
## Just an Ordinary and Easy-to-use Mac OS file manager
Navigate files fast using partial searches with no additional text

Click `return` to go into a directory, open a file, or use a command

Clicking `return` on a partial search will select the first option in the suggestions

Clicking `tab` will autofill the partial search with the first option in the suggestions

Enter `..` to go back to the parent directory

Navigate through previous commands using `up arrow` and `down arrow`

Use `-> <dirname>` to jump to an existing directory anywhere inside the current directory
- Variables can be used in place of directory names
- Commands cannot be used while jumping

Access commands -> `::`

## Command list:

- clear
- cmd
- copyto
- currdir
- editor
- info
- list
- moveto
- new
- newdir
- purge
- quit
- remove
- rename
- run
- variable
- varlist

clear - clear screen
- Usage: `::clear`

cmd - run custom bash command in new terminal
- Usage: `::cmd >> <bash command>`

Command runs in current directory by default
To run in a different directory use `cd <dirname> &&` before running the command
- Example:
`::cmd >> cd path/to/preferred/directory && <bash command>`

copyto - copy contents of file or directory to new file or directory
- Usage: `<filename>::copyto >> <destination>`

currdir - display path to current directory
- Usage: `::currdir`

editor - open file or directory in preferred editor
- Usage: `<filename>::editor >> <file editor>`

info - display file or directory information
- Usage: `<filename>::info`

list - list all files and directories in directory
- Usage: `<dirname>::list` or `::list`

moveto - move file or directory to existing directory
- Usage: `<filename>::moveto >> <destination>`

new - create new file
- Usage: `<filename>::new`

newdir - create new directory
- Usage: `<dirname>::newdir`

purge - remove existing directory and its contents
- Usage: `<dirname>::purge`

quit - quit the terminal
- Usage: `::quit`

remove - remove existing file or directory
- Usage: `<filename or dirname>::remove`

rename - rename existing file or directory
- Usage: `<filename or dirname>::rename >> <newfilename or newdirname>`

run - run a script
- Usage: `<filename>::run`

variable - create and set variable with custom value
- Usage: `::variable >> <varname> >> <value>`

To access variables anywhere in the query, use `$<varname>`
- Example:
```
::variable >> newfilename >> new.txt
old.txt::rename >> $newfilename
```

Variables can only be used in command arguments

'CURRDIR' is a default variable with its value being the current directory
- It can be accessed anytime with `$CURRDIR`

User defined variables get cleared after every session

varlist - list all variables
- Usage: `::varlist`
