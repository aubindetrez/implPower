// Documentation about this module is located in
// Documentation/BranchUnit.md
`timescale 100ps / 100ps

module BranchUnit (
    input logic i_clk,
    input logic i_rst,
    input logic i_32b_mode,
    input logic i_stall,  // Stalls: Do not update the nia

    // From/To Instruction Fetch
    output logic [0:63] o_next_instr_addr,  // Address of the next instruction

    // From/To Instruction Identify
    input logic [0:31] i_instr,  // output instruction to the branch unit
    input logic i_en,  // Enable branch unit
    input logic i_i_form,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_b_form,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_cond_LR,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_cond_CTR,  // if o_bu_en is set, indication the BU what form is the instr.
    input logic i_cond_TAR,  // if o_bu_en is set, indication the BU what form is the instr.

    // From/To the Register File
    input logic [0:31] i_condition_register,  // Section 2.3.1
    input logic [0:63] i_target_address_register,  // Section 2.3.2
    output logic [0:63] o_count_register,  // Section 2.3.3
    output logic [0:63] o_link_register,  // Section 2.3.3

    // Debug and Error
    output logic err_branch_on_stall,  // we should not get a new instruction to process on a stall
    output logic dbg_invalid_instruction,  // Debug: the instruction is invalid
    output logic dbg_unknown_branch  // Debug: Cannot identify the instruction
);
  logic boot;  // Set after reset to make sure we start with address 0
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) boot <= 1'b1;
    else boot <= 1'b0;
  end

  logic [0:63] cia;  // Current Instruction Address
  logic [0:63] nia;  // Next Instruction Address
  assign o_next_instr_addr = nia;
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) cia <= 64'b0;
    else if (i_stall == 1'b0) cia <= nia;
  end

  // Error description: What if i_stall is set and we do not update
  // cia but receive i_en/i_instr, we'll lose
  // nia
  assign err_branch_on_stall = i_stall & i_en;

  logic decr_ctr;  // 1'b1 if ctr need to be decremented
  assign decr_ctr = ~bo[2] & (i_b_form | i_cond_LR | i_cond_TAR);  // See ISA Section 2.4
  logic [0:63] ctr_d, ctr_q;  // Count Register
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) ctr_q <= 64'b0;
    else ctr_q <= ctr_d;
  end
  assign ctr_d = (decr_ctr == 1'b1) ? ctr_q - 1 : ctr_q;
  assign o_count_register = ctr_q;
  logic ctr_d_null;
  assign ctr_d_null = (ctr_d == 64'b0) ? 1 : 0;
  logic a_ctr_q;
  assign a_ctr_q = {ctr_q[0:61], 2'b00};  // aligned

  // For Branch Conditional B-form, specifies the CTR bit to be tested
  logic [0:4] bi;
  assign bi = i_instr[11:15];

  logic lk;
  assign lk = i_instr[31];
  // If LK=1 -> then save current address+4 in the Link Register (LR)
  // (regardless of whether the branch is taken)
  logic [0:63] lr_d, lr_q;  // Link Register
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) lr_q <= 64'b0;
    else lr_q <= lr_d;
  end
  // (1) Invalid instructions should not change any state (register)
  assign lr_d = (i_en == 1'b1 && lk == 1'b1 && invalid_bcctr_form == 1'b0) ? cia + 4 : lr_q;
  assign o_link_register = lr_q;

  logic [0:25] li;  // LI field in a Branch I-form instruction, see Section 2.4
  assign li = {i_instr[6:29], 2'b00};  // LI << 2
  logic [0:63] exts_li;  // Sign extended LI
  assign exts_li = {{38{li[0]}}, li};  // LI[0] is the MSB (and the sign)

  logic [0:63] a_lr_q;  // The LR register aligned
  assign a_lr_q = {lr_q[0:61], 2'b00};  // aligned

  logic [0:63] a_tar;  // The TAR register aligned
  assign a_tar = {i_target_address_register[0:61], 2'b00};

  logic aa;  // AA field in a Branch instruction (all forms) see Section 2.4
  assign aa = i_instr[30];

  // TODO: If the "decrement and test CTR" options is specified (BO2) the instruction is invalid
  logic invalid_bcctr_form;
  assign invalid_bcctr_form = i_cond_CTR & ~bo[2];
  assign dbg_invalid_instruction = invalid_bcctr_form;
  // TODO Formal: check no write on register can happen with an invalid instruction

  // See Power ISA Section 2.5 Figure 40
  // for b-form branch and bclr (Branch Conditional to Link Register)
  logic branch_taken;
  always_comb begin
    unique case (bo) inside
      5'b0000?: branch_taken = ~ctr_d_null & ~i_condition_register[bi];
      5'b0001?: branch_taken = ctr_d_null & ~i_condition_register[bi];
      5'b001??: branch_taken = ~i_condition_register[bi];
      5'b0100?: branch_taken = ~ctr_d_null & i_condition_register[bi];
      5'b0101?: branch_taken = ctr_d_null & i_condition_register[bi];
      5'b011??: branch_taken = i_condition_register[bi];
      5'b1?00?: branch_taken = ~ctr_d_null;
      5'b1?01?: branch_taken = ctr_d_null;
      5'b1?1??: branch_taken = 1'b1;
      default:  branch_taken = 1'b0;
    endcase
  end

  // TODO high order 32bits set to 0 in 32 bit mode
  always_comb begin
    if (i_en == 1'b1) begin  // This is a branch
      if (i_i_form == 1'b1) begin
        if (aa == 1'b0) begin
          // TODO Reuse the 64b adder (and check if the synthesis does
          // a good job)
          nia = exts_li + cia;  // CIA = address of the current instruction
          // TODO high order 32bits set to 0 in 32 bit mode
        end else begin
          nia = exts_li;
          // TODO high order 32bits set to 0 in 32 bit mode
        end
      end else if (i_b_form == 1'b1) begin
        if (branch_taken == 1'b1) begin
          if (aa == 1'b0) begin
            nia = exts_bd + cia;
            // TODO high order 32bits set to 0 in 32 bit mode
          end else begin
            nia = exts_bd;
            // TODO high order 32bits set to 0 in 32 bit mode
          end
        end else nia = cia + 4;  // Branch is not taken: sequential instructions
      end else if (i_cond_LR == 1'b1) begin
        if (branch_taken == 1'b1) begin
          nia = a_lr_q;  // LR register, aligned
          // TODO high order 32bits set to 0 in 32 bit mode
        end else nia = cia + 4;  // Branch is not taken: sequential instructions
      end else if (i_cond_CTR == 1'b1) begin
        if (invalid_bcctr_form == 1'b1)
          nia = cia + 4;  // TODO (1) branch to custom error recovery handler
        else if (branch_taken == 1'b1) nia = a_ctr_q;
        else nia = cia + 4;
      end else if (i_cond_TAR == 1'b1) begin
        if (branch_taken == 1'b1) nia = a_tar;  // TAR register, aligned
        else nia = cia + 4;  // Branch is not taken: sequential instructions
      end else nia = cia + 4;  // Also raises (2)
    end else begin  // Not a branch
      if (boot == 1'b1) nia = cia;
      else nia = cia + 4;  // sequential instructions
    end
  end
  assign dbg_unknown_branch = i_en & ~(i_i_form | i_b_form | i_cond_LR | i_cond_CTR | i_cond_TAR);

  logic [0:15] bd;
  assign bd = {i_instr[16:29], 2'b00};  // BD << 2
  logic [0:63] exts_bd;
  assign exts_bd = {{48{bd[0]}}, bd};  // BD[0] is the MSB (and the sign)

  // For Branch Conditional instruction, the BO field specifies the condition
  // For Branch Conditional B-form (see Power ISA section 2.4)
  logic [0:4] bo;  // Branch condition
  assign bo = i_instr[6:10];

  // Software hit whether the branch is likely to be taken
  // See Power ISA section 2.4
  logic [0:1] at;  // Branch likeliness
  // 00 -> No hint is given
  // 01 -> Reserved
  // 10 -> The branch is very likely not to be taken
  // 11 -> The branch is very likely to be taken
  always_comb begin
    unique case (bo) inside
      5'b0000?: at = 2'b00;
      5'b0001?: at = 2'b00;
      5'b001??: at = bo[3:4];
      5'b0100?: at = 2'b00;
      5'b0101?: at = 2'b00;
      5'b011??: at = bo[3:4];
      5'b1?00?: at = {bo[1], bo[4]};
      5'b1?01?: at = {bo[1], bo[4]};
      5'b1?1??: at = 2'b11;
      default:  at = 2'b00;
    endcase
  end

  logic is_target_addr_hint_valid;
  assign is_target_addr_hint_valid = i_cond_LR | i_cond_CTR | i_cond_TAR;
  // TODO Set this signal if the instruction is one of:
  // - Branch conditional to link register
  // - Branch conditional to count register
  // - Branch conditional to target address register

  // See Power ISA Section 2.4
  // BH=00 AND blrc -> (00)
  // BH=00 AND bcctr, bctar -> (01)
  // BH=01 AND bclr -> (01)
  // BH=10 Reserved -> (11)
  // BH=11 AND bclr, bcctr, bctar -> (10)
  // This signal is valid if is_target_addr_hint_valid is 1'b1
  logic [0:1] target_addr_cond_hint;  // Target Address hints for Conditional Branches (aka BH)
  // 00 -> Subroutine return
  // 01 -> Likely to be the same as the last time the branch was taken
  // 10 -> Not Predictable
  // 11 -> Reserved

  // TODO Add coverage points to make sure we cover:
  // - B-Branch and the 9 options for BO
  // - B-Branch and the 2 options for at


  initial begin
    $dumpfile("trace.vcd");
    $dumpvars(0, BranchUnit);
    #1;
  end

`ifdef FORMAL
  // Used by formal verification to check not check $past(...) on initial conditions
  logic f_past_valid;
  initial f_past_valid = 1'b0;
  always @(posedge i_clk) f_past_valid <= 1'b1;

  always @(posedge i_clk) begin
    assume (i_rst == 1'b0);

    // We assume no instruction is sent (i_en) while the cpu is stalled (i_stall)
    if (i_stall == 1'b1) assume (i_en == 1'b0);

    // When no branch occurs -> Run sequential instructions
    if (f_past_valid == 1'b1 && $past(i_en) == 1'b0) begin
      assert ($past(cia) == cia + 4);
    end

    // When stalled, the Current Instruction Address CIA, do not change
    if (f_past_valid == 1'b1 && $past(i_stall) == 1'b0) begin
      assert ($past(cia) == cia);
    end
  end
`endif

endmodule
