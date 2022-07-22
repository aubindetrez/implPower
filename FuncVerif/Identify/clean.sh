echo "Cleaning System Verilog Sim"
rm -rf sv_bin sv.log trace.vcd

echo "Cleaning Python Sim"
make clean_all
