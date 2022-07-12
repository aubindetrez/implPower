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
    output logic dbg_is_prefixed,
    output logic dbg_is_branch_i_form,
    output logic dbg_is_branch_b_form,
    output logic dbp_is_branch_cond_to_LR,
    output logic dbp_is_branch_cond_to_CTR,
    output logic dbp_is_branch_cond_to_TAR
);
  logic is_prefixed;
  logic [5:0] primary_opcode;

  assign primary_opcode = i_instr[5:0];  // Power ISA v3.1 Section 1.6.1

  // Detect if [0:31] is an prefix - Power ISA Section 1.6.3
  assign is_prefixed = (primary_opcode == 6'b100000) ? 1'b1 : 1'b0;
  assign dbg_is_prefixed = is_prefixed;

  // TODO send branch instructions to the branch decoding unit
  logic is_branch_i_form;
  logic is_branch_b_form;
  logic is_branch_xl_form;
  logic is_branch_cond_to_LR;  // Conditional branch to Link Register, Section 2.4
  logic is_branch_cond_to_CTR;  // Conditional branch to Count Register, Section 2.4
  logic is_branch_cond_to_TAR;  // Conditional branch to Target Address Register, Section 2.4
  assign is_branch_i_form = (primary_opcode == 6'b000110) ? 1'b1 : 1'b0;
  assign dbg_is_branch_i_form = is_branch_i_form;
  assign is_branch_b_form = (primary_opcode == 6'b011010) ? 1'b1 : 1'b0;
  assign dbg_is_branch_b_form = is_branch_b_form;
  assign is_branch_xl_form = (primary_opcode == 6'b100110) ? 1'b1 : 1'b0;
  // According to Section 2.4, bits [21, 31] = 0x16 -> 0001_0110
  assign is_branch_cond_to_LR = (is_branch_xl_form == 1'b1
                                    && i_instr[30:21] == 10'b0110100000)? 1'b1: 1'b0;
  // According to Section 2.4, bits [21, 31] = 0x528 -> 0101_0010_1000
  // radare2: 2104804e bctrl
  // 0018297c       cmpd r9, r3
  // 2000804e       blr
  assign is_branch_cond_to_CTR = (is_branch_xl_form == 1'b1
                                    && i_instr[30:21] == 10'b0101001010)? 1'b1: 1'b0;
  assign is_branch_cond_to_TAR = (is_branch_xl_form == 1'b1
                                    && i_instr[30:21] == 10'b0001101010)? 1'b1: 1'b0;
  assign dbp_is_branch_cond_to_LR = is_branch_cond_to_LR;
  assign dbp_is_branch_cond_to_CTR = is_branch_cond_to_CTR;
  assign dbp_is_branch_cond_to_TAR = is_branch_cond_to_TAR;

  // TODO continue with identifying other instructions
endmodule
