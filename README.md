- <ins>J</ins>ust an <ins>O</ins>rdinary and <ins>E</ins>asy-to-use <ins>MA</ins>c OS file <ins>MA</ins>nager
- Requires Python 3
  
## Just an Ordinary and Easy-to-use Mac OS file manager
- Navigate files fast using partial searches with no additional text
- Click `return` to go into a directory, open a file, or use a command
- Clicking `return` on a pertial search will select the first option in the suggestions
- Clicking `tab` will autofill the partial search with the first option in the suggestions
- Enter `..` to go back to the parent directory

- Access commands -> `::`

## Command list:
- clear
- copyto
- currdir
- editor
- list
- meta
- moveto
- new
- newdir
- remove
- rename
- runcmd
- variable

clear - clear screen
- Usage: `::clear`

copyto - copy file to existing file or directory
- Usage: `<filename>::copyto >> <destination>`

currdir - display path to current directory
- Usage: `::currdir`

editor - open file or directory in preferred editor
- Usage: `<filename>::editor >> <file editor>`

list - list all files and directories in directory
- Usage: `<dirname>::list` or `::list`

meta - display metadata of file or directory
- Usage: `<filename>::meta`

moveto - move file to existing directory
- Usage: `<filename>::moveto >> <destination>`

new - create new file
- Usage: `<filename>::new`

newdir - create new directory
- Usage: `<dirname>::newdir`

remove - remove existing file or directory
- Usage: `<filename or dirname>::remove`

rename - rename existing file or directory
- Usage: `<filename or dirname>::rename >> <newfilename or newdirname>`

runcmd - run custom bash command in new terminal
- Usage: `::runcmd >> <bash command>`

Command runs in current directory by default
To run in a different directory use `cd <dirname> &&` before running the command
- Example:
`::runcmd >> cd path/to/preferred/directory && <bash command>`

variable - create and set variable with custom value
- Usage: `::variable >> <varname> >> <value>`

To access variables anywhere in the query, use `$<varname>`
- Example:
```
::variable >> newfilename >> new.txt
old.txt::rename >> $newfilename
```
