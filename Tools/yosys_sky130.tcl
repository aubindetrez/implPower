# Usage:
# SYNTH_OUTPUT=... TOP_LEVEL=... VLOG_FILE_NAME=.../dut.v yosys yosys_ng45.tcl

# compare to the previous version on a 64b adder
# a[0] -> o[63] 9.39 data arrival time
# a[0] -> o[63] 4.40 data arrival time (match OpenLane's results)

proc pause {{message "Hit Enter to continue ==> "}} {
    puts -nonewline $message
    flush stdout
    gets stdin
}

yosys read_verilog $::env(VLOG_FILE_NAME)
yosys hierarchy -check
pause;
yosys tribuf
yosys synth -top $::env(TOPLEVEL) -flatten
yosys share -aggressive
yosys opt
yosys opt_clean -purge

yosys techmap -map "$::env(SKY130A)/libs.tech/openlane/sky130_fd_sc_hd/tribuff_map.v"
yosys simplemap
# Convert design to logical gate-level netlists
yosys techmap -map "$::env(SKY130A)/libs.tech/openlane/sky130_fd_sc_hd/latch_map.v"
yosys simplemap
# Map internal register types to the ones form the cell library
yosys dfflibmap -liberty "$::env(SKY130A)/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
# Use ABC to map remaining logic to cells from the cell library
yosys abc -D 10000.0 -constr sky130.sdc -liberty "$::env(SKY130A)/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib" -script {+read_constr,sky130.sdc;fx;mfs;strash;refactor;balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance;retime,-D,{D},-M,5;scleanup;fraig_store; balance; fraig_store; balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance; fraig_store; balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance; fraig_store; balance; rewrite; refactor; balance; rewrite; rewrite,-z; balance; refactor,-z; rewrite,-z; balance; fraig_store; fraig_restore;amap,-m,-Q,0.1,-F,20,-A,20,-C,5000;retime,-D,{D};&get,-n;&st;&dch;&nf;&put;buffer,-N,5,-S,750.0;upsize,{D};dnsize,{D};stime,-p;print_stats -m} -showtmp
yosys setundef -zero
yosys hilomap -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO
yosys splitnets
yosys opt_clean -purge
yosys insbuf -buf sky130_fd_sc_hd__buf_2 A X
yosys write_verilog -noattr -noexpr -nohex -nodec -defparam $::env(SYNTH_OUTPUT)
pause;
