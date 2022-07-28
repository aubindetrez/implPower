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
    input logic [0:31] i_instr,

    output logic [0:31] o_instr_suffix,
    output logic [0:31] o_instr_prefix,

    // Instruction identification
    output logic o_branch_identified,
    output logic o_condreg_identified,

    // Additional information
    output logic o_branch_i_form,
    output logic o_branch_b_form,
    output logic o_branch_cond_LR,
    output logic o_branch_cond_CTR,
    output logic o_branch_cond_TAR,

    // Additional information
    output logic o_condreg_crand,
    output logic o_condreg_crnand,
    output logic o_condreg_cror,
    output logic o_condreg_crxor,
    output logic o_condreg_crnor,
    output logic o_condreg_creqv,
    output logic o_condreg_crandc,
    output logic o_condreg_crorc,
    output logic o_condreg_mcrf
);
  logic is_prefixed;
  logic [0:5] primary_opcode;

  // 6 most signification bits are the OPcode according to Power ISA v3.1 Section 1.6.3
  assign primary_opcode = i_instr[0:5];

  // Detect if [0:31] is an prefix - Power ISA Section 1.6.3
  assign is_prefixed = (primary_opcode == 6'b000001) ? 1'b1 : 1'b0;

  // If the i_instr is prefixed and the module is enabled,
  // latch i_instr and next cycle we can decode a prefixed instruction
  // {prefix, suffix}
  logic [0:31] suffix;
  assign suffix = i_instr;
  logic [0:31] prefix_q, prefix_d;
  always_ff @(posedge i_clk or posedge i_rst) begin
      if (i_rst == 1'b1) prefix_q <= 32'b0;
      else if (i_en == 1'b1) prefix_q <= prefix_d;
  end
  assign prefix_d = (is_prefixed == 1'b1)? i_instr: 32'b0;
  assign o_instr_suffix = suffix;
  assign o_instr_prefix = prefix_q;

  logic is_branch_i_form;
  logic is_branch_b_form;
  logic is_branch_xl_form;
  logic is_branch_cond_to_LR;  // Conditional branch to Link Register, Section 2.4
  logic is_branch_cond_to_CTR;  // Conditional branch to Count Register, Section 2.4
  logic is_branch_cond_to_TAR;  // Conditional branch to Target Address Register, Section 2.4
  assign is_branch_i_form = (primary_opcode == 6'b010010) ? 1'b1 : 1'b0;  // Decimal: 18
  assign is_branch_b_form = (primary_opcode == 6'b010000) ? 1'b1 : 1'b0;  // Decimal: 16
  assign is_branch_xl_form = (primary_opcode == 6'b010011) ? 1'b1 : 1'b0;  // Decimal: 19
  // According to Section 2.4, bits [21, 31] = 16 = 0x10 = 0b00_0001_0000
  assign is_branch_cond_to_LR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b0000010000)? 1'b1: 1'b0;
  // According to Section 2.4, bits [21, 31] = 528 = 0x210 = 0b10_0001_0000
  assign is_branch_cond_to_CTR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b1000010000)? 1'b1: 1'b0;
  // According to Section 2.4, bits [21, 31] = 560 = 0x230 = 0b10_0011_0000
  assign is_branch_cond_to_TAR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b1000110000)? 1'b1: 1'b0;


  assign o_branch_identified = is_branch_i_form | is_branch_b_form | is_branch_cond_to_LR
                            | is_branch_cond_to_CTR | is_branch_cond_to_TAR;
  assign o_branch_i_form = is_branch_i_form;
  assign o_branch_b_form = is_branch_b_form;
  assign o_branch_cond_LR = is_branch_cond_to_LR;
  assign o_branch_cond_CTR = is_branch_cond_to_CTR;
  assign o_branch_cond_TAR = is_branch_cond_to_TAR;

  assign o_condreg_identified = o_condreg_crand | o_condreg_crnand | o_condreg_cror | o_condreg_crxor |
                        o_condreg_crnor | o_condreg_creqv | o_condreg_crandc| o_condreg_crorc |
                        o_condreg_mcrf;
  assign o_condreg_crand = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b01_0000_0001)? 1'b1: 1'b0; // Decimal 257
  assign o_condreg_crnand = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b00_1110_0001)? 1'b1: 1'b0; // Decimal 225
  assign o_condreg_cror = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b01_1100_0001)? 1'b1: 1'b0; // Decimal 449
  assign o_condreg_crxor = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b00_1100_0001)? 1'b1: 1'b0; // Decimal 193
  assign o_condreg_crnor = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b00_0010_0001)? 1'b1: 1'b0; // Decimal 33
  assign o_condreg_creqv = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b01_0010_0001)? 1'b1: 1'b0; // Decimal 289
  assign o_condreg_crandc = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b00_1000_0001)? 1'b1: 1'b0; // Decimal 129
  assign o_condreg_crorc = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b01_1010_0001)? 1'b1: 1'b0; // Decimal 417
  assign o_condreg_mcrf = (is_branch_xl_form == 1'b1
                                && i_instr[21:30] == 10'b00_0000_0000)? 1'b1: 1'b0; // Decimal 0

`ifdef FORMAL
  always @(posedge i_clk) begin
    // Making sure an instruction is not identified both as Conditional Register and as Branch
    if (o_condreg_identified == 1'b1) assert (o_branch_identified == 1'b0);
    if (o_branch_identified == 1'b1) assert (o_condreg_identified == 1'b0);

    // Unique instruction is detected
    if (o_condreg_identified == 1'b1)
      assert (o_condreg_crand + o_condreg_crnand + o_condreg_cror
                                          + o_condreg_crxor + o_condreg_crnor + o_condreg_creqv
                                          + o_condreg_crandc+ o_condreg_crorc
                                          + o_condreg_mcrf == 1);
    // Unique instruction is detected
    if (o_branch_identified == 1'b1)
      assert(is_branch_i_form + is_branch_b_form + is_branch_cond_to_LR
                                          + is_branch_cond_to_CTR + is_branch_cond_to_TAR == 1);
  end
`endif

  initial begin
    $dumpfile("trace.vcd");
    $dumpvars(0, Identify);
    #1;
  end
endmodule
