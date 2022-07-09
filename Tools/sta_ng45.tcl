# Usage:
# SYNTH_OUTPUT=... TOP_LEVEL=... sta sta_ng45.tcl

proc pause {{message "Hit Enter to continue ==> "}} {
    puts -nonewline $message
    flush stdout
    gets stdin
}

sta read_liberty $::env(NANGATE45)/lib/NangateOpenCellLibrary_typical.lib
sta read_verilog $::env(SYNTH_OUTPUT)
sta link_design $::env(TOPLEVEL)
sta set_units -time ns
sta report_power
puts "This power information may not be accurate, placing and routing + spice (ngspice) simulation if required for more accurate results"
pause;
sta report_checks -unconstrained  -fields {slew trans net cap input_pin}
puts "This delay estimate may not be accurate, physical design and parasitic extraction would be much more accurate"
puts "You can type \"exit\" when you are done"
