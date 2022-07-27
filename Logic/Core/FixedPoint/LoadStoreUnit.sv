// This file contains the hardware description for:
// - the Fixed-Point Load Instructions (Power ISA section 3.3.2)
// - the 64-bit Fixed-Point Load Instructions (Power ISA section 3.3.2.1)
`timescale 100ps / 100ps

module LoadStoreUnit (
    input logic i_clk,
    input logic i_rst,
    input logic i_32b_mode,
    input logic i_en,
    input logic i_stall,

    input logic [0:31] i_instr_prefix,  // first 32 MSB from the 64b preffixed instruction
    input logic [0:31] i_instr_suffix,  // 32 LSB from the 64b preffixed instruction

    output logic [0:4] o_rf1_addr,  // address to index the register file (RF)
    // If simultaneous read and write, the old value is read
    output logic o_rf1_enr,  // enable read from the register file
    output logic o_rf1_enw,  // enable write to the register file

    output logic [0:4] o_rf2_addr,  // address to index the register file (RF)
    // If simultaneous read and write, the old value is read
    output logic o_rf2_enr,  // enable read from the register file
    output logic o_rf2_enw,  // enable write to the register file

    output logic [0:63] o_data_addr,  // address to read from the main memory (Data cache)
    // If simultaneous read and write, the old value is read
    output logic o_data_enr,  // enable read from the data cache
    output logic o_data_enw,  // enable write to the data cache

    input logic i_is_op34,  // Can be a lbz or plbz instruction
    input logic [0:63] i_cia,  // Current Instruction Address (CIA)

    // PLBZ: if R is equal to 1 and RA is not equal to 0, the instruction form if invalid
    output logic err_invalid_load_instr,

    // Request all pipeline to stall because more than 1 cycle is needed to perform load/store
    output logic o_stall
);
  // fields from the instruction's suffix
  logic [0:5] ra;
  assign ra = i_instr_suffix[11:15];
  logic [0:5] rt;
  assign rt = i_instr_suffix[6:10];
  logic [0:15] d1;
  assign d1 = i_instr_suffix[16:31];

  // fields from the instruction's prefix
  logic [0:5] prefix_op;
  assign prefix_op = i_instr_prefix[0:5];
  logic r;
  assign r = i_instr_prefix[11];  // valid when is_plbz == 1'b1
  logic [0:17] d0;
  assign d0 = i_instr_prefix[14:31];


  logic is_ra_null;
  assign is_ra_null = (ra == 6'b000000) ? 1'b1 : 1'b0;
  logic is_prefixed;
  assign is_prefixed = (prefix_op == 6'b000001) ? 1'b1 : 1'b0;
  logic is_plbz;
  assign is_plbz = i_is_op34 & is_prefixed;
  logic is_plbz_w_r;
  assign is_plbz_w_r = is_plbz & r;
  logic is_plbz_wo_r;
  assign is_plbz_wo_r = is_plbz & ~r;

  assign err_invalid_load_instr = is_plbz_w_r & ~is_ra_null;

  logic [0:63] exts_d1;  // EXTS64(D)
  assign exts_d1 = {{48{d1[0]}}, d1};
  logic [0:63] exts_d0d1;  // EXTS64(d0||d1)
  assign exts_d0d1 = {{30{d0[0]}}, {d0, d1}};


  logic [0:63] effective_address;  // also called EA, used to index (data) memory

  // Create a trace file
  initial begin
    $dumpfile("trace.vcd");
    $dumpvars(0, LoadStoreUnit);
    #1;
  end

  // Using formal verification to perform sanitary checks
`ifdef FORMAL
  // Used by formal verification to avoid $past(...) on initial conditions
  logic f_past_valid;
  initial f_past_valid = 1'b0;
  always @(posedge i_clk) f_past_valid <= 1'b1;

  always @(posedge i_clk) begin
    assume (i_rst == 1'b0);

    // Inputs do not change if o_stall is set before all cpu is stalled
    if (o_stall == 1'b1) assume ($stable(i_cia));
    if (o_stall == 1'b1) assume ($stable(i_is_op34));
    if (o_stall == 1'b1) assume ($stable(i_32b_mode));

    // We cannot write if i_stall is set
    if (f_past_valid == 1'b1 && $past(i_stall) == 1'b1) assert (o_rf_enw == 1'b0);
    if (f_past_valid == 1'b1 && $past(i_stall) == 1'b1) assert (o_data_enw == 1'b0);

    // No read from the register file if no new instruction is to be executed
    if (i_en == 1'b0) assert (o_rf_enr == 1'b0);
    // No write to the register file if no new instruction is to be executed
    if (i_en == 1'b0) assert (o_rf_enw == 1'b0);
    // No read from the data cache if no new instruction is to be executed
    if (i_en == 1'b0) assert (o_data_enr == 1'b0);
    // No write to the data cache if no new instruction is to be executed
    if (i_en == 1'b0) assert (o_data_enw == 1'b0);
  end
`endif

endmodule
