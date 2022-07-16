#!/usr/bin/env bash
# This script checks if any file has been deleted or renamed in `git status`
# And warns you if any file in the repository still refers to the old name
gitroot="`git rev-parse --show-toplevel`"

deleted_files=`git ls-files --deleted --full-name`
for file in $deleted_files
do
    references=`grep -nIr "$file" "$gitroot"`
    num_refs=`echo $references | wc -l`
    if ! [ $num_refs -eq 0 ]
    then
        echo ">>> You deleted or renamed file: $file"
        echo ">>> But you also need to fix all references to it:"
        echo "$references"
        exit 1
    fi
done

exit 0 # return success