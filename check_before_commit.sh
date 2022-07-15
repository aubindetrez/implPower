gitroot="`git rev-parse --show-toplevel`"
cd $gitroot

if ! command -v python3 &> /dev/null
then
    echo "Error: You do not have Python installed"
    exit 1
fi
all_py_files=`find . -name "*.py"`
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
    verible-verilog-lint $file
    if [[ $? -ne 0 ]]
    then echo "==> Check failed, please fix it and try again"
        exit 1
    fi
done

# Run all Functional tests by calling "make" in every directories in FuncVerif/
for dir in FuncVerif/*
do echo ">>> Running Functional tests for $dir"
    cd $dir
    ./test.sh
    if ! [ $? -eq 0 ]
    then
        echo ">>> Verification failed while testing $dir"
        echo ">>> Please fix it and try again"
        echo ">>> Stopping the simulation (so you cannot miss it ;) )"
        exit 1
    fi
    ./clean.sh
    cd $gitroot
done
