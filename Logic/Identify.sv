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

    // To/From BRanch Unit (BRU)
    output logic [0:31] o_bru_instr,  // output instruction to the branch unit
    output logic o_bru_en,  // Enable branch unit
    output logic o_bru_i_form,  // if o_bru_en is set, indication the BU what form is the instr.
    output logic o_bru_b_form,  // if o_bru_en is set, indication the BU what form is the instr.
    output logic o_bru_cond_LR,  // if o_bru_en is set, indication the BU what form is the instr.
    output logic o_bru_cond_CTR,  // if o_bru_en is set, indication the BU what form is the instr.
    output logic o_bru_cond_TAR,  // if o_bru_en is set, indication the BU what form is the instr.
    
    output logic o_condreg_en, // i_instr is a condition register Instruction
    output logic [0:31] o_condreg_instr, // output instruction to the CondReg Unit
    output logic o_condreg_crand, // Instruction is a Condition Register AND
    output logic o_condreg_crnand, // Instruction is a Condition Register NAND
    output logic o_condreg_cror, // Instruction is a Conditon Register OR
    output logic o_condreg_crxor, // Instruction is a Condition Register XOR
    output logic o_condreg_crnor, // Instruction is a Condition Register NOR
    output logic o_condreg_creqv, // Instruction is a Condition Register Equivalent
    output logic o_condreg_crandc, // Instruction is a Condition Register AND with Complement
    output logic o_condreg_crorc, // Instruction is a Conditon Register OR with Complement
    output logic o_condreg_mcrf // Instruction is a Move Conditoin Register Field
);
  logic is_prefixed;
  logic [0:5] primary_opcode;

  // 6 most signification bits are the OPcode according to Power ISA v3.1 Section 1.6.3
  assign primary_opcode = i_instr[0:5];

  // Detect if [0:31] is an prefix - Power ISA Section 1.6.3
  assign is_prefixed = (primary_opcode == 6'b000001) ? 1'b1 : 1'b0;

  logic is_branch_i_form;
  logic is_branch_b_form;
  logic is_branch_xl_form;
  logic is_branch_cond_to_LR;  // Conditional branch to Link Register, Section 2.4
  logic is_branch_cond_to_CTR;  // Conditional branch to Count Register, Section 2.4
  logic is_branch_cond_to_TAR;  // Conditional branch to Target Address Register, Section 2.4
  assign is_branch_i_form = (primary_opcode == 6'b010010) ? 1'b1 : 1'b0; // Decimal: 18
  assign is_branch_b_form = (primary_opcode == 6'b010000) ? 1'b1 : 1'b0; // Decimal: 16
  assign is_branch_xl_form = (primary_opcode == 6'b010011) ? 1'b1 : 1'b0; // Decimal: 19
  // According to Section 2.4, bits [21, 31] = 16 = 0x10 = 0b00_0001_0000
  assign is_branch_cond_to_LR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b0000010000)? 1'b1: 1'b0;
  // According to Section 2.4, bits [21, 31] = 528 = 0x210 = 0b10_0001_0000
  assign is_branch_cond_to_CTR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b1000010000)? 1'b1: 1'b0;
  // According to Section 2.4, bits [21, 31] = 560 = 0x230 = 0b10_0011_0000
  assign is_branch_cond_to_TAR = (is_branch_xl_form == 1'b1
                                    && i_instr[21:30] == 10'b1000110000)? 1'b1: 1'b0;


  assign o_bru_en = is_branch_i_form | is_branch_b_form | is_branch_cond_to_LR
                            | is_branch_cond_to_CTR | is_branch_cond_to_TAR;
  assign o_bru_i_form = is_branch_i_form;
  assign o_bru_b_form = is_branch_b_form;
  assign o_bru_cond_LR = is_branch_cond_to_LR;
  assign o_bru_cond_CTR = is_branch_cond_to_CTR;
  assign o_bru_cond_TAR = is_branch_cond_to_TAR;
  assign o_bru_instr = i_instr[0:31];

  assign o_condreg_instr = i_instr[0:31];
  assign o_condreg_en = o_condreg_crand | o_condreg_crnand | o_condreg_cror | o_condreg_crxor |
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
        if (o_condreg_en == 1'b1) assert (o_bru_en == 1'b0);

        // Unique instruction is detected
        if (o_condreg_en == 1'b1) assert (o_condreg_crand + o_condreg_crnand + o_condreg_cror
                                          + o_condreg_crxor + o_condreg_crnor + o_condreg_creqv
                                          + o_condreg_crandc+ o_condreg_crorc + o_condreg_mcrf == 1);
        // Unique instruction is detected
        if (o_bru_en == 1'b1) assert(is_branch_i_form + is_branch_b_form + is_branch_cond_to_LR
                                          + is_branch_cond_to_CTR + is_branch_cond_to_TAR == 1);
    end
`endif

  initial begin
    $dumpfile("trace.vcd");
    $dumpvars(0, Identify);
    #1;
  end
endmodule
