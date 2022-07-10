gitroot="`git rev-parse --show-toplevel`"
cd $gitroot

# Run Linter on all SystemVerilog files
if ! command -v verible-verilog-lint &> /dev/null
then
    echo "Error: verible-verilog-lint is not installed on your system"
    echo "You can get it from: https://github.com/chipsalliance/verible"
    echo "Make sure it is in your PATH before trying again"
    exit 1
fi
for file in `find ./Logic/ -name "*.sv"`
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
    make
    # TODO FIXME Stop if the test fails (we do not want to miss it)
    make clean_all
    cd $gitroot
done
