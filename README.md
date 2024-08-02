- <ins>J</ins>ust an <ins>O</ins>rdinary and <ins>E</ins>asy-to-use <ins>MA</ins>c OS file <ins>MA</ins>nager
- Requires Python 3
- Just an Ordinary and Easy-to-use Mac OS file manager\r

Navigate files fast using partial searches with no additional text\r

Click 'return' to go into a directory, open a file, or use a command\r

Clicking 'return' on a pertial search will select the first option in the suggestions\r

Clicking 'tab' will autofill the partial search with the first option in the suggestions\r

Enter `..` to go back to the parent directory\r

Access commands -> `::`\r

Command list:\r

clear\r
copyto\r
currdir\r
editor\r
list\r
meta\r
moveto\r
new\r
newdir\r
remove\r
rename\r
runcmd\r
variable\r

clear - clear screen\r
Usage: `::clear`\r

copyto - copy file to existing file or directory\r
Usage: `<filename>::copyto >> <destination>`\r

currdir - display path to current directory\r
Usage: `::currdir`\r

editor - open file or directory in preferred editor\r
Usage: `<filename>::editor >> <file editor>`\r

list - list all files and directories in directory\r
Usage: `<dirname>::list` or `::list`\r

meta - display metadata of file or directory\r
Usage: `<filename>::meta`\r

moveto - move file to existing directory\r
Usage: `<filename>::moveto >> <destination>`\r

new - create new file\r
Usage: `<filename>::new`\r

newdir - create new directory\r
Usage: `<dirname>::newdir`\r

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
