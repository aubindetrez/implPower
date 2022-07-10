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
  // if LK=1 then save branch's address+4 in the Link Register (LR)
  // Evaluate branch condition (BO field) see section 2.4

endmodule
