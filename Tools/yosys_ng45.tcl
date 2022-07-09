# Usage:
# SYNTH_OUTPUT=... TOP_LEVEL=... VLOG_FILE_NAME=.../dut.v yosys yosys_ng45.tcl

# compare to the previous version on a 64b adder
# a[0] -> o[63] 2.2 data arrival time
# a[0] -> o[63] 0.76 data arrival time

proc pause {{message "Hit Enter to continue ==> "}} {
    puts -nonewline $message
    flush stdout
    gets stdin
}

yosys read_verilog $::env(VLOG_FILE_NAME)
yosys hierarchy -check
pause;
#yosys proc; yosys opt; yosys memory; yosys opt; yosys fsm; yosys opt
yosys tribuf
yosys synth -top $::env(TOPLEVEL) -flatten
yosys share -aggressive
yosys opt
yosys opt_clean -purge
# Convert design to logical gate-level netlists
yosys techmap -map "$::env(NANGATE45)/cells_*"
yosys simplemap
# Map internal register types to the ones form the cell library
yosys dfflibmap -liberty "$::env(NANGATE45)/lib/NangateOpenCellLibrary_typical.lib"
# Use ABC to map remaining logic to cells from the cell library
yosys abc -D 10000.0 -constr ng45.sdc -liberty "$::env(NANGATE45)/lib/NangateOpenCellLibrary_typical.lib" -script {+read_constr,ng45.sdc;fx;mfs;strash;refactor;balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance;retime,-D,{D},-M,5;scleanup;fraig_store; balance; fraig_store; balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance; fraig_store; balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance; fraig_store; balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance; fraig_store; fraig_restore;amap,-m,-Q,0.1,-F,20,-A,20,-C,5000;retime,-D,{D};&get,-n;&st;&dch;&nf;&put;buffer,-N,5,-S,750.0;upsize,{D};dnsize,{D};stime,-p;print_stats -m} -showtmp
yosys setundef -zero
yosys splitnets
yosys opt_clean -purge
# insert buffer cells
yosys insbuf -buf BUF_X2 A X
yosys write_verilog -noattr -noexpr -nohex -nodec -defparam $::env(SYNTH_OUTPUT)
pause;
