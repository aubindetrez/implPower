// SystemVerilog verification code
// This is independant from the Python verif. code

`include "../../Logic/Identify.sv"
`timescale 100ps / 100ps

module test_Identify;
  logic clk = 1'b0;
  logic rst = 1'b1;
  logic en = 1'b0;
  logic [0:63] instr = 64'b0;
  logic [0:31] bru_instr;  // output instruction to the branch unit
  logic bru_en;  // Enable branch unit
  logic bru_i_form;  // if o_bru_en is set, indication the BU what form is the instr.
  logic bru_b_form;  // if o_bru_en is set, indication the BU what form is the instr.
  logic bru_cond_LR;  // if o_bru_en is set, indication the BU what form is the instr.
  logic bru_cond_CTR;  // if o_bru_en is set, indication the BU what form is the instr.
  logic bru_cond_TAR;  // if o_bru_en is set, indication the BU what form is the instr.

  always #10 clk = ~clk;

  Identify UUT (
      .i_clk(clk),
      .i_rst(rst),
      .i_en(en),
      .i_instr(instr),
      .o_bru_instr(bru_instr),
      .o_bru_en(bru_en),
      .o_bru_i_form(bru_i_form),
      .o_bru_b_form(bru_b_form),
      .o_bru_cond_LR(bru_cond_LR),
      .o_bru_cond_CTR(bru_cond_CTR),
      .o_bru_cond_TAR(bru_cond_TAR)
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
    assert (bru_instr == 32'b01001000000000110010101111111011);
    assert (bru_en == 1'b1);  // It is a branch
    assert (bru_i_form == 1);  // It is a I-form
    assert (bru_b_form == 0);
    assert (bru_cond_LR == 0);
    assert (bru_cond_CTR == 0);
    assert (bru_cond_TAR == 0);
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
