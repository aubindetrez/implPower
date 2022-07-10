// Documentation about this module is in Documentation/Idenfity.md
`timescale 100ps / 100ps

// TODO Instructions to Identify: (Section 1.10.3)
// - Load/Store (Can be prefixed)
// - Reg/Reg (Can be prefixed)
// - Is a branch


module Identify (
    input logic i_clk,
    input logic i_rst,
    input logic i_en,
    input logic [63:0] i_instr,
    output logic dbg_is_prefixed
);
  logic is_prefixed;
  logic [5:0] primary_opcode;

  assign primary_opcode = i_instr[5:0];  // Power ISA v3.1 Section 1.6.1

  // Detect if [0:31] is an prefix - Power ISA Section 1.6.3
  assign is_prefixed = (primary_opcode == 6'b100000) ? 1'b1 : 1'b0;
  assign dbg_is_prefixed = is_prefixed;

  // TODO send branch instructions to the branch decoding unit

  // TODO continue with identifying other instructions
endmodule
