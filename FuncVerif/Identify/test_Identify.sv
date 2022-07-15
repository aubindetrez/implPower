// SystemVerilog verification code
// This is independant from the Python verif. code

`include "../../Logic/Identify.sv"
`timescale 100ps / 100ps

module test_Identify;
  logic clk = 1'b0;
  logic rst = 1'b1;
  logic en = 1'b0;
  logic [0:63] instr = 64'b0;
  logic [0:31] bu_instr;  // output instruction to the branch unit
  logic bu_en;  // Enable branch unit
  logic bu_i_form;  // if o_bu_en is set, indication the BU what form is the instr.
  logic bu_b_form;  // if o_bu_en is set, indication the BU what form is the instr.
  logic bu_cond_LR;  // if o_bu_en is set, indication the BU what form is the instr.
  logic bu_cond_CTR;  // if o_bu_en is set, indication the BU what form is the instr.
  logic bu_cond_TAR;  // if o_bu_en is set, indication the BU what form is the instr.

  always #10 clk = ~clk;

  Identify UUT (
      .i_clk(clk),
      .i_rst(rst),
      .i_en(en),
      .i_instr(instr),
      .o_bu_instr(bu_instr),
      .o_bu_en(bu_en),
      .o_bu_i_form(bu_i_form),
      .o_bu_b_form(bu_b_form),
      .o_bu_cond_LR(bu_cond_LR),
      .o_bu_cond_CTR(bu_cond_CTR),
      .o_bu_cond_TAR(bu_cond_TAR)
  );

  initial begin
    $dumpfile("/tmp/trace.vcd");
    $dumpvars(0, UUT);
    rst = 1'b1;
    en  = 1'b0;

    @(posedge clk);
    #1;
    rst = 1'b0;
    en  = 1'b1;
    $display("Resset sequence done");

    instr = {32'b01001000000000110010101111111011, 32'b0};
    #1;
    assert (bu_instr == 32'b01001000000000110010101111111011);
    assert (bu_en == 1'b1);  // It is a branch
    assert (bu_i_form == 1);  // It is a I-form
    assert (bu_b_form == 0);
    assert (bu_cond_LR == 0);
    assert (bu_cond_CTR == 0);
    assert (bu_cond_TAR == 0);
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
