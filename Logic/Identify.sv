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
    input logic [0:63] i_instr,
    output logic [0:31] o_bu_instr,  // output instruction to the branch unit
    output logic o_bu_en,  // Enable branch unit
    output logic o_bu_i_form,  // if o_bu_en is set, indication the BU what form is the instr.
    output logic o_bu_b_form,  // if o_bu_en is set, indication the BU what form is the instr.
    output logic o_bu_cond_LR,  // if o_bu_en is set, indication the BU what form is the instr.
    output logic o_bu_cond_CTR,  // if o_bu_en is set, indication the BU what form is the instr.
    output logic o_bu_cond_TAR  // if o_bu_en is set, indication the BU what form is the instr.
);
  logic is_prefixed;
  logic [0:5] primary_opcode;

  // 6 most signification bits are the OPcode according to Power ISA v3.1 Section 1.6.3
  assign primary_opcode = i_instr[0:5];

  // Detect if [0:31] is an prefix - Power ISA Section 1.6.3
  assign is_prefixed = (primary_opcode == 6'b000001) ? 1'b1 : 1'b0;

  // TODO send branch instructions to the branch decoding unit
  logic is_branch_i_form;
  logic is_branch_b_form;
  logic is_branch_xl_form;
  logic is_branch_cond_to_LR;  // Conditional branch to Link Register, Section 2.4
  logic is_branch_cond_to_CTR;  // Conditional branch to Count Register, Section 2.4
  logic is_branch_cond_to_TAR;  // Conditional branch to Target Address Register, Section 2.4
  assign is_branch_i_form = (primary_opcode == 6'b010010) ? 1'b1 : 1'b0;
  assign is_branch_b_form = (primary_opcode == 6'b010000) ? 1'b1 : 1'b0;
  assign is_branch_xl_form = (primary_opcode == 6'b010011) ? 1'b1 : 1'b0;
  // According to Section 2.4, bits [21, 31] = 16 = 0x10 = 0b00_0001_0000
  assign is_branch_cond_to_LR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b0000010000)? 1'b1: 1'b0;
  // According to Section 2.4, bits [21, 31] = 528 = 0x210 = 0b10_0001_0000
  assign is_branch_cond_to_CTR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b1000010000)? 1'b1: 1'b0;
  // According to Section 2.4, bits [21, 31] = 560 = 0x230 = 0b10_0011_0000
  assign is_branch_cond_to_TAR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b1000110000)? 1'b1: 1'b0;
  assign o_bu_en = is_branch_i_form | is_branch_b_form | is_branch_cond_to_LR
                            | is_branch_cond_to_CTR | is_branch_cond_to_TAR;
  assign o_bu_i_form = is_branch_i_form;
  assign o_bu_b_form = is_branch_b_form;
  assign o_bu_cond_LR = is_branch_cond_to_LR;
  assign o_bu_cond_CTR = is_branch_cond_to_CTR;
  assign o_bu_cond_TAR = is_branch_cond_to_TAR;
  assign o_bu_instr = i_instr[0:31];

  // TODO continue with identifying other instructions
  initial begin
    $dumpfile("trace.vcd");
    $dumpvars(0, Identify);
    #1;
  end
endmodule
