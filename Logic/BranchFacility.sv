// Documentation about this module is located in
// Documentation/BranchFacility.md
`timescale 100ps / 100ps

module BranchFacility (
    input logic i_clk,
    input logic i_rst,
    input logic i_en,  // Enable
    input logic i_32b_mode,
    input logic [63:0] i_instr,
    output logic [63:0] o_next_instr_addr,  // Address of the next instruction
    input logic i_is_branch,
    input logic i_is_branch_to_link_register,
    input logic [31:0] i_condition_register,  // Section 2.3.1
    input logic [63:0] i_link_register,  // Section 2.3.2
    input logic [63:0] i_count_register  // Section 2.3.3
);
  // TODO decode what kind of branch is it
  // - Branch with I/B-form instruction + AA (is it an offset?)
  // - Branch with XL-form + is it LR or CTR

  // Section 2.4 describe 5 operations
  // - Add a displacement to the branch address (branch or branch cond. AA=0)
  // - Use an absolute address (branch or branch cond. AA=1)
  // - Use the Link Register (branch cond. to LR)
  // - Use the Count Register (branch cond. to CTR)
  // - Use the Target Address Register (branch cond. to TAR)

  // TODO execute: compute the effective address (Next Instruction Address)
  // TODO update next_instr_addr accordingly

  // TODO
  logic provide_return_addr;  // LK=1 -> return address is to be provided
  // if LK=1 then save branch's address+4 in the Link Register (LR)
  // (regardless of whether the branch is taken)


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

endmodule
