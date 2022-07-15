// Documentation about this module is located in
// Documentation/BranchFacility.md
`timescale 100ps / 100ps

module BranchFacility (
    input logic i_clk,
    input logic i_rst,
    input logic i_32b_mode,
    input logic i_stall,  // Stalls: Do not update the nia

    // From/To Instruction Fetch
    output logic [63:0] o_next_instr_addr,  // Address of the next instruction

    // From/To Instruction Identify
    input logic [31:0] i_instr,  // output instruction to the branch unit
    input logic i_en,  // Enable branch unit
    input logic i_i_form,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_b_form,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_cond_LR,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_cond_CTR,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_cond_TAR,  // if o_bu_en is set, indication the BU what form is the instr.

    // From/To the Register File
    input logic [31:0] i_condition_register,  // Section 2.3.1
    input logic [63:0] i_target_address_register,  // Section 2.3.2
    input logic [63:0] i_count_register,  // Section 2.3.3
    output logic [63:0] o_link_register,  // Section 2.3.3

    // Debug and Error
    output logic err_branch_on_stall  // we should not get a new instruction to process on a stall
);
  logic boot;  // Set after reset to make sure we start with address 0
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) boot <= 1'b1;
    else boot <= 1'b0;
  end

  // TODO use _d and _q here?
  logic [63:0] cia;  // Current Instruction Address
  logic [63:0] nia;  // Next Instruction Address

  assign o_next_instr_addr = nia;
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) cia <= 64'b0;
    else if (i_stall == 1'b0) cia <= nia;
  end

  assign err_branch_on_stall = i_stall & i_en;
  // Error description: What if i_stall is set and we do not update
  // cia but receive i_en/i_instr, we'll lose
  // nia

  logic lk;
  assign lk = i_instr[31];
  // If LK=1 -> then save current address+4 in the Link Register (LR)
  // (regardless of whether the branch is taken)

  logic [63:0] lr_d;  // next Link Register
  logic [63:0] lr_q;  // Link Register
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) lr_q <= 64'b0;
    else lr_q <= lr_d;
  end
  assign lr_d = {<<1{le_lr_d}};
  assign o_link_register = lr_q;

  logic [63:0] le_lr_d;
  assign le_lr_d = (i_en == 1'b1 && lk == 1'b1) ? le_cia + 4 : le_lr_q;
  logic [63:0] le_lr_q;
  assign le_lr_q = {<<1{lr_q}};

  logic [25:0] li;  // LI field in a Branch I-form instruction, see Section 2.4
  assign li = {2'b00, i_instr[29:6]};  // LI << 2
  logic [63:0] exts_li;  // Sign extended LI
  assign exts_li = {li, {38{li[0]}}};  // LI[0] is the MSB and the sign

  logic aa;  // AA field in a Branch instruction (all forms) see Section 2.4
  assign aa = i_instr[30];

  logic [63:0] le_exts_li;  // LittleEndian version of exts_li
  assign le_exts_li = {<<1{exts_li}};  // Swap endianess, now MSB is [63]
  logic [63:0] le_cia;
  assign le_cia = {<<1{cia}};
  logic [63:0] le_nia;
  assign nia = {<<1{le_nia}};

  always_comb begin
    if (i_en == 1'b1) begin  // This is a branch
      if (i_i_form == 1'b1) begin
        if (aa == 1'b0) begin
          // TODO Reuse the 64b adder (and check if the synthesis does
          // a good job)
          le_nia = le_exts_li + le_cia;  // CIA = address of the current instruction
          // TODO high order 32bits set to 0 in 32 bit mode
        end else begin
          le_nia = le_exts_li;
          // TODO high order 32bits set to 0 in 32 bit mode
        end
      end
      // TODO Other kind of branch
    end else begin  // Not a branch
      if (boot == 1'b1) le_nia = le_cia;
      else le_nia = le_cia + 4;  // sequential instructions
    end
  end


  logic is_branch_conditional;  // 1'b1 if it is a branch conditional instruction
  // assign is_branch_conditional = TODO

  // For Branch Conditional instruction, the BO field specifies the condition
  // see Power ISA section 2.4
  logic [4:0] branch_condition;  // Also called BO
  // assign branch_condition = ...

  // Software hit whether the branch is likely to be taken or not (called 'at')
  // See Power ISA section 2.4
  logic [1:0] branch_likeliness;
  // 00 -> No hint is given
  // 01 -> Reserved
  // 10 -> The branch is very likely not to be taken
  // 11 -> The branch is very likely to be taken
  always_comb begin
    unique case (branch_condition) inside
      5'b0000?: branch_likeliness = 2'b00;  // No hint
      5'b0001?: branch_likeliness = 2'b00;  // No hint
      5'b001??: branch_likeliness = branch_condition[1:0];
      5'b0100?: branch_likeliness = 2'b00;  // No hint
      5'b0101?: branch_likeliness = 2'b00;  // No hint
      5'b011??: branch_likeliness = branch_condition[1:0];
      5'b1?00?: branch_likeliness = {branch_condition[3], branch_condition[0]};
      5'b1?01?: branch_likeliness = {branch_condition[3], branch_condition[0]};
      5'b1?1??: branch_likeliness = 2'b11;  // Always taken
      default:  branch_likeliness = 2'b00;  // No hint
    endcase
  end

  logic is_branch_to_reg;
  // TODO Set this signal if the instruction is one of:
  // - Branch conditional to link register
  // - Branch conditional to count register
  // - Branch conditional to target address register

  // This signal is valid if is_branch_to_reg is 1'b1
  logic [1:0] target_address_hint;  // Also called BH field
  // See Power ISA Section 2.4
  // 00 AND blrc -> subroutine return
  // 00 AND bcctr, bctar -> address is likely to be the same as the last
  //                                              time the branch was taken
  // 01 AND bclr -> address is likely to be the same as the alst time the
  //                                                        branch was taken
  // 10 Reserved
  // 11 AND bclr, bcctr, bctar -> target address it not predictable

  initial begin
    $dumpfile("trace.vcd");
    $dumpvars(0, BranchFacility);
    #1;
  end

endmodule
