#!/usr/bin/env bash

gitroot="`git rev-parse --show-toplevel`"
cd $gitroot
REPORT="" # Summary


# Check file references in Documentation
echo ">>> Checking if you deleted/renamed a file and didn't update documentation..."
$gitroot/Tools/check_file_refs.sh
if [[ $? -ne 0 ]] # Last command didn't return SUCCESS (0)
then echo "==> Please fix it and try again"
    exit 1
fi

# Warn about likely outdated documentation
$gitroot/Tools/warn_doc_update.sh
if [[ $? -ne 0 ]] # Last command didn't return SUCCESS (0)
then echo "==> Fix it and try again"
    exit 1
fi

# Check Python syntax
if ! command -v python3 &> /dev/null
then
    echo "Error: You do not have Python installed"
    exit 1
fi
all_py_files=`find $gitroot -name "*.py"`
for file in $all_py_files
do
    echo ">>> Checking Python syntax on $file"
    python3 -c "import ast; ast.parse(open(\"$file\").read())"
    if [[ $? -ne 0 ]]
    then echo "==> Error in you python file $file, fix it and try again."
        exit 1
    fi
done

# Run formatter on all SystemVerilog files to ensure a consistence reading
# experience to all contributors
if ! command -v verible-verilog-format &> /dev/null
then
    echo "Error: verible-verilog-format is not installed on your system"
    echo "You can get it from: https://github.com/chipsalliance/verible"
    echo "Make sure it is in your PATH before trying again"
    exit 1
fi
for file in `find ./ -name "*.sv"`
do echo ">>> Running formatter on $file"
    verible-verilog-format --inplace $file
    if [[ $? -ne 0 ]]
    then echo "==> Error while formatting, please fix it and try again"
        exit 1
    fi
done

# Run Linter on all SystemVerilog files
if ! command -v verible-verilog-lint &> /dev/null
then
    echo "Error: verible-verilog-lint is not installed on your system"
    echo "You can get it from: https://github.com/chipsalliance/verible"
    echo "Make sure it is in your PATH before trying again"
    exit 1
fi
for file in `find ./ -name "*.sv"`
do echo ">>> Running Linter on $file"
    verible-verilog-lint --rules=-packed-dimensions-range-ordering,-unpacked-dimensions-range-ordering $file
    if [[ $? -ne 0 ]]
    then echo "==> Check failed, please fix it and try again"
        exit 1
    fi
done

REPORT="$REPORT \n High Level Model's tests:"
cd $gitroot
# Run all High Level Model tests by executing test.sh in every directories in HLModel/
for test_file in `find $gitroot/HLModel/ -name "test.sh"`
do  dir=`dirname $test_file`
    REPORT="$REPORT \n    - $dir   "
    echo ">>> Running Unit tests on the High Level Model (HLModel) for $dir"
    cd $dir
    ./test.sh
    if ! [ $? -eq 0 ]
    then
        REPORT="$REPORT FAILED"
        echo ">>> Verification failed while testing $dir"
        echo ">>> Please fix it and try again"
        echo ">>> Stopping the simulation (so you cannot miss it ;) )"
        exit 1
    fi
    REPORT="$REPORT PASSED"
    if [ -x ./clean.sh ]
    then ./clean.sh
    fi
    cd $gitroot
done

REPORT="$REPORT \n Functional Verification tests:"
cd $gitroot
# Run all Functional tests by executing test.sh in every directories in FuncVerif/
for test_file in `find $gitroot/FuncVerif/ -name "test.sh"`
do  dir=`dirname $test_file`
    REPORT="$REPORT \n    - $dir   "
    echo ">>> Running Functional tests for $dir"
    cd $dir
    ./test.sh
    if ! [ $? -eq 0 ]
    then
        REPORT="$REPORT FAILED"
        echo ">>> Verification failed while testing $dir"
        echo ">>> Please fix it and try again"
        echo ">>> Stopping the simulation (so you cannot miss it ;) )"
        exit 1
    fi
    REPORT="$REPORT PASSED"
    if [ -x ./clean.sh ]
    then ./clean.sh
    fi
    cd $gitroot
done

REPORT="$REPORT \n Formal Verification tests:"
cd $gitroot
# Run all Formal tests by executing test.sh in every directories in FormalVerif/
for test_file in `find $gitroot/FormalVerif/ -name "test.sh"`
do  dir=`dirname $test_file`
    REPORT="$REPORT \n    - $dir   "
    echo ">>> Running Formal tests for $dir"
    cd $dir
    ./test.sh
    if ! [ $? -eq 0 ]
    then
        REPORT="$REPORT FAILED"
        echo ">>> Verification failed while testing $dir"
        echo ">>> Please fix it and try again"
        echo ">>> Stopping the simulation (so you cannot miss it ;) )"
        exit 1
    fi
    REPORT="$REPORT PASSED"
    if [ -x ./clean.sh ]
    then ./clean.sh
    fi
    cd $gitroot
done

echo -e "$REPORT" # Print a Summary
