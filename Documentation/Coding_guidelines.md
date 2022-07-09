# Verilog coding guideline

In order to be compatible with opensource EDA tools (yosys, iverilog, verilator...)
We program using SystemVerilog and convert it to Verilog using `sv2v`.
```verilog
// Only use comments with "//" do not use "/* ... */"
    // Only indent with spaces, no tabulation because of some weird
    // with propriatory tools

module <MODULE'S NAME> #(
    parameter integer <PARAMETER'S NAME> = ... // only use [A-Z_0-9] for constant's names
) (
    input logic <INPUT'S NAME>,
    output logic <INPUT'S NAME>
);

logic [<SIZE>-1:0] <WIRE'S NAME>; // use little endian for packed arrays
logic <WIRE'S NAME> [<SIZE>-1]; // use big endian for unpacked arrays

// use "assign" statements (with blocking '=') for combinational logic
assign <SOME WIRE> = <...>;

// if using assign is unpractical use combinational blocks
always_comb
begin
    // Only use blocking statements
    a = b; // Such a simple assigment should use "assign"
end

always_ff
begin
    // do not use casex and prefer case inside over casez
    unique case inside (select)
        2b'00: e = 1'b0;
        2b'01: e = ...;
        default: e = ...; // set defaults even if not required
    endcase
end

// always name your "generate" (if / for...) statements

assign big_bit_vector[7:0] = {4'b0000, smaller_vector[3:0]}; // be explicit

assign counter[3:0] = 4'(counter_q + 4'b1); // explicitely discard the carry

// Write a testcase using cocotb in verification/<MODULE'S NAME> for every module
// At least check you can synthetise using yosys (default "synth" or AIG)
```
