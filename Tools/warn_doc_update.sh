#!/usr/bin/env bash
# This script asks you for confirmation if you modified a SystemVerilog file in Logic/
# And if a file called the same in Documentation/ has not been updated
gitroot="`git rev-parse --show-toplevel`"

list_modified=`git ls-files --modified --full-name $gitroot`

for file in $list_modified
do
    if [[ "$file" =~ ^Logic/.*\.sv$ ]]
    then
        # Look if there is a file in Documentation/ called the same
        base=`basename "$file"` # Remove Logic/
        base="${base%.sv}" # Remove the .sv
        if ! [ -f "$gitroot/Documentation/$base.md" ]
        then break # Documentation not found; continue with the next file
        fi
        
        # Check the Documentation/... file is also inside $list_modified
        grep "Documentation/$base.md" <<< "$list_modified" > /dev/null
        if ! [ $? -eq 0 ]
        then echo ">>> You edited $file"
            echo ">>> But you didn't update Documentation/$base.md"
            cmd=" "; while [ "$cmd" != "yes" -a "$cmd" != "no" ]
            do read -p ">>> Is it ok? [yes/no] " cmd
            done
            if [ "$cmd" = "no" ]
            then exit 1
            fi
        fi
    fi
done