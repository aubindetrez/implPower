./clean.sh

sby LoadStoreUnit.sby # symbiyosys
if ! [ $? -eq 0 ]
then
    exit 1
fi

exit 0
