# Usage:
# SYNTH_OUTPUT=... TOP_LEVEL=... VLOG_FILE_NAME=.../dut.v yosys yosys_xil.tcl

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
yosys synth_xilinx -top $::env(TOPLEVEL) -flatten
yosys share -aggressive
yosys opt
yosys opt_clean -purge
yosys stat
yosys show
#yosys write_verilog $::env(SYNTH_OUTPUT)
pause;
