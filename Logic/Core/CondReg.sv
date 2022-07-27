module CondReg (
    input logic i_clk,
    input logic i_rst,

    input logic i_en,  // i_instr is a condition register Instruction
    input logic [0:31] i_instr,  // output instruction to the CondReg Unit
    input logic i_crand,  // Instruction is a Condition Register AND
    input logic i_crnand,  // Instruction is a Condition Register NAND
    input logic i_cror,  // Instruction is a Conditon Register OR
    input logic i_crxor,  // Instruction is a Condition Register XOR
    input logic i_crnor,  // Instruction is a Condition Register NOR
    input logic i_creqv,  // Instruction is a Condition Register Equivalent
    input logic i_crandc,  // Instruction is a Condition Register AND with Complement
    input logic i_crorc,  // Instruction is a Conditon Register OR with Complement
    input logic i_mcrf,  // Instruction is a Move Conditoin Register Field

    output logic [0:31] o_cr  // Condition Register (CR)
);

  logic [0:31] cr_d, cr_q;
  always_ff @(posedge i_clk or posedge i_rst) begin
    if (i_rst == 1'b1) cr_q <= 32'b0;
    else if (i_en == 1'b1) cr_q <= cr_d;
  end
  assign o_cr = cr_q;

  logic [0:4] bt;
  assign bt = i_instr[6:10];  // Instruction operand: A bit's offset in CR
  logic [0:4] ba;
  assign ba = i_instr[11:15];  // Instruction operand: A bit's offset in CR
  logic [0:4] bb;
  assign bb = i_instr[16:20];  // Instruction operand: A bit's offset in CR

  // Perform the bitwise operation on the bit selected by BT
  logic int_d;
  assign int_d = (i_crand == 1'b1)?  cr_q[ba] & cr_q[bb] :
                    (i_crnand == 1'b1)? ~(cr_q[ba] & cr_q[bb]) :
                    (i_cror == 1'b1)? cr_q[ba] | cr_q[bb] :
                    (i_crxor == 1'b1)? cr_q[ba] ^ cr_q[bb] :
                    (i_crnor == 1'b1)? ~(cr_q[ba] | cr_q[bb]) :
                    (i_creqv == 1'b1)? ~(cr_q[ba] ^ cr_q[bb]) :
                    (i_crandc == 1'b1)? cr_q[ba] & ~cr_q[bb] :
                    (i_crorc == 1'b1)? cr_q[ba] | ~cr_q[bb]:
                    cr_q[bt]; // Default: Do not modify any bit

  logic [0:31] int_cr;
  genvar i;
  for (i = 0; i < 32; i++) begin : gen_condreg
    assign int_cr[i] = (bt == i) ? int_d : cr_q[i];
  end

  logic [0:2] bf;
  assign bf = i_instr[6:8];
  logic [0:2] bfa;
  assign bfa = i_instr[11:13];
  logic [0:4] bfa_sht;
  assign bfa_sht = {bfa, 2'b00};

  // On the result from the previous operation, Perform the Move Condition Register
  //assign cr_d[0] = (i_mcrf == 1'b1 && bf == 0)? int_cr[bfa*4]: int_cr[0];
  //assign cr_d[1] = (i_mcrf == 1'b1 && bf == 0)? int_cr[bfa*4+1]: int_cr[1];
  //assign cr_d[2] = (i_mcrf == 1'b1 && bf == 0)? int_cr[bfa*4+2]: int_cr[2];
  //assign cr_d[3] = (i_mcrf == 1'b1 && bf == 0)? int_cr[bfa*4+3]: int_cr[3];

  //assign cr_d[4] = (i_mcrf == 1'b1 && bf == 1)? int_cr[bfa*4]: int_cr[4];
  //assign cr_d[5] = (i_mcrf == 1'b1 && bf == 1)? int_cr[bfa*4+1]: int_cr[5];
  //assign cr_d[6] = (i_mcrf == 1'b1 && bf == 1)? int_cr[bfa*4+2]: int_cr[6];
  //assign cr_d[7] = (i_mcrf == 1'b1 && bf == 1)? int_cr[bfa*4+3]: int_cr[7];
  // [...]

  // TODO synthesis and optimize
  genvar i;
  for (i = 0; i < 32; i++) begin : gen_mcrf
    assign cr_d[i] = (i_mcrf == 1'b1 && bf == i / 4) ? int_cr[bfa_sht+i%4] : int_cr[i];
  end

  initial begin
    $dumpfile("trace.vcd");
    $dumpvars(0, CondReg);
    #1;
  end

`ifdef FORMAL
  // Used by formal verification to check not check $past(...) on initial conditions
  logic f_past_valid;
  initial f_past_valid = 1'b0;
  always @(posedge i_clk) f_past_valid <= 1'b1;

  always @(posedge i_clk) begin
    assume (i_rst == 1'b0);
    if (i_en == 1'b1) begin
      // Making sure 'mcrf BF, BFA' with BF == BFA will not change CR
      assume (i_crand + i_crnand + i_cror + i_crxor + i_crnor
                                + i_creqv + i_crandc + i_crorc + i_mcrf == 1);
      if (f_past_valid == 1'b1 && $past(i_mcrf) == 1'b1 && $past(bf) == $past(bfa))
        assert ($past(o_cr) == o_cr);
    end
    // If not enabled, CR should not change
    if (f_past_valid == 1'b1 && $past(i_en) == 1'b0) assert ($past(o_cr) == o_cr);
  end
`endif

endmodule
