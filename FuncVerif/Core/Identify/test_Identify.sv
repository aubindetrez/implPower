// SystemVerilog verification code
// This is independant from the Python verif. code

`include "../../../Logic/Core/Identify.sv"
`timescale 100ps / 100ps

module test_Identify;
  logic clk = 1'b0;
  logic rst = 1'b1;
  logic en = 1'b0;
  logic [0:31] instr = 32'b0;
  logic [0:31] instr_suffix;
  logic [0:31] instr_prefix;
  logic stall_fetch_arb;
  logic arb_full_mask;
  logic branch_identified;
  logic condreg_identified;
  logic unknown_instr;
  logic branch_i_form;
  logic branch_b_form;
  logic branch_cond_LR;
  logic branch_cond_CTR;
  logic branch_cond_TAR;
  logic condreg_crand;
  logic condreg_crnand;
  logic condreg_cror;
  logic condreg_crxor;
  logic condreg_crnor;
  logic condreg_creqv;
  logic condreg_crandc;
  logic condreg_crorc;
  logic condreg_mcrf;

  always #10 clk = ~clk;

  Identify UUT (
      .i_clk(clk),
      .i_rst(rst),
      .i_en(en),
      .i_instr(instr),
      .o_instr_suffix(instr_suffix),
      .o_instr_prefix(instr_prefix),
      .i_arb_full_mask(arb_full_mask),
      .o_stall_fetch_arb(stall_fetch_arb),
      .o_branch_identified(branch_identified),
      .o_condreg_identified(condreg_identified),
      .o_unknown_instr(unknown_instr),
      .o_branch_i_form(branch_i_form),
      .o_branch_b_form(branch_b_form),
      .o_branch_cond_LR(branch_cond_LR),
      .o_branch_cond_CTR(branch_cond_CTR),
      .o_branch_cond_TAR(branch_cond_TAR),
      .o_condreg_crand(condreg_crand),
      .o_condreg_crnand(condreg_crnand),
      .o_condreg_cror(condreg_cror),
      .o_condreg_crxor(condreg_crxor),
      .o_condreg_crnor(condreg_crnor),
      .o_condreg_creqv(condreg_creqv),
      .o_condreg_crandc(condreg_crandc),
      .o_condreg_crorc(condreg_crorc),
      .o_condreg_mcrf(condreg_mcrf)
  );

  initial begin
    $dumpfile("/tmp/trace.vcd");
    $dumpvars(0, UUT);
    rst = 1'b1;
    en = 1'b0;
    instr = 32'b0;
    arb_full_mask = 1'b0;

    @(posedge clk);
    #1;
    rst = 1'b0;
    en  = 1'b1;
    $display("Resset sequence done");

    instr = 32'b01001000000000110010101111111011;
    #1;
    assert (instr_prefix == 32'b0);
    assert (instr_suffix == 32'b01001000000000110010101111111011);
    assert (branch_identified == 1'b1);  // It is a branch
    assert (unknown_instr == 1'b0);
    assert (condreg_identified == 1'b0);
    assert (branch_i_form == 1);  // It is a I-form
    assert (branch_b_form == 0);
    assert (branch_cond_LR == 0);
    assert (branch_cond_CTR == 0);
    assert (branch_cond_TAR == 0);
    $display("Simulation done");
    @(posedge clk);
    #1;
    @(posedge clk);
    #1;
    @(posedge clk);
    #1;
    #1000;
    $finish;
  end
endmodule
