./clean.sh
ln -s ../../Logic/Identify.sv Identify.sv

sby Identify.sby # symbiyosys
if ! [ $? -eq 0 ]
then
    exit 1
fi

exit 0
