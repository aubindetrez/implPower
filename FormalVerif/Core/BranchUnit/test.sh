gitroot="`git rev-parse --show-toplevel`"
./clean.sh
sv2v --define=FORMAL $gitroot/Logic/Core/BranchUnit.sv > BranchUnit.v

sby BranchUnit.sby # symbiyosys
if ! [ $? -eq 0 ]
then
    exit 1
fi

exit 0
