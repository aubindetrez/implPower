./clean.sh
sv2v --define=FORMAL ../../Logic/BranchFacility.sv > BranchFacility.v

sby BranchFacility.sby # symbiyosys
if ! [ $? -eq 0 ]
then
    exit 1
fi

exit 0
