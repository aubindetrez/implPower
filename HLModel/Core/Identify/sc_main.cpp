// Documentation about this module can be found in Documentation/Identify.md

#include <systemc.h>
#include <iostream>

// Monitors the DUT's output
SC_MODULE(Monitor)
{
    sc_in<bool> i_clk;

    sc_in<bool> i_rst;
    sc_in<bool> i_en;
    sc_in<sc_bv<32>> i_instr;
    sc_in<bool> i_arb_full_mask;

    sc_in<sc_bv<32>> i_instr_prefix;
    sc_in<sc_bv<32>> i_instr_suffix;
    sc_in<bool> i_branch_identified;
    sc_in<bool> i_branch_i_form;
    sc_in<bool> i_branch_b_form;
    sc_in<bool> i_branch_cond_lr;
    sc_in<bool> i_branch_cond_ctr;
    sc_in<bool> i_branch_cond_tar;
    sc_in<bool> i_stall_fetch_arb;
    sc_in<bool> i_condreg_identified;
    sc_in<bool> i_condreg_crand;
    sc_in<bool> i_condreg_crnand;
    sc_in<bool> i_condreg_cror;
    sc_in<bool> i_condreg_crxor;
    sc_in<bool> i_condreg_crnor;
    sc_in<bool> i_condreg_creqv;
    sc_in<bool> i_condreg_crandc;
    sc_in<bool> i_condreg_crorc;
    sc_in<bool> i_condreg_mcrf;

    void MonGen()
    {
        // TODO check outputs
        std::cout << sc_time_stamp() << std::endl;
    }
    SC_CTOR(Monitor)
    {
        SC_METHOD(MonGen);
        // Monitor is called when an instruction is identified
        sensitive << i_branch_identified;
        sensitive << i_condreg_identified;
        // Or when a new instruction is to be processed
        sensitive << i_instr;
    }
};

// Generates stimulus
SC_MODULE(Stimulus)
{
    sc_in<bool> i_clk;
    sc_out<bool> o_rst;
    sc_out<bool> o_en;
    sc_out<sc_bv<32>> o_instr;
    sc_out<bool> o_arb_full_mask;

    // Called every positive edge (i_clk) cf #1
    void StimGen()
    {
        // Reset sequence
        o_instr.write(0);
        o_arb_full_mask.write(false);
        o_rst.write(true);
        o_en.write(false);
        wait(12, SC_NS);
        o_rst.write(false);
        wait(3, SC_NS);
        o_en.write(true);

        // Send random instructions
        for (int i=0; i<100; i++) {
            wait(); // Next clock cycle instruction 0 is fetched
            wait(7, SC_NS); // Some time for the cache to return an instruction
            std::cout<<"Send random instruction"<<std::endl;
            // TODO
        }

        sc_stop(); // End simulation
    }
    SC_CTOR(Stimulus)
    {
        SC_THREAD(StimGen);
        sensitive << i_clk.pos(); // #1
    }
};

SC_MODULE(Identify)
{
    sc_in<bool> i_clk;
    sc_in<bool> i_rst;
    sc_in<bool> i_en;
    sc_in<sc_bv<32>> i_instr;

    sc_out<sc_bv<32>> o_instr_prefix;
    sc_out<sc_bv<32>> o_instr_suffix;

    sc_out<bool> o_branch_identified;
    sc_out<bool> o_branch_i_form;
    sc_out<bool> o_branch_b_form;
    sc_out<bool> o_branch_cond_lr;
    sc_out<bool> o_branch_cond_ctr;
    sc_out<bool> o_branch_cond_tar;

    sc_out<bool> o_stall_fetch_arb;
    sc_in<bool> i_arb_full_mask;

    sc_out<bool> o_condreg_identified;
    sc_out<bool> o_condreg_crand;
    sc_out<bool> o_condreg_crnand;
    sc_out<bool> o_condreg_cror;
    sc_out<bool> o_condreg_crxor;
    sc_out<bool> o_condreg_crnor;
    sc_out<bool> o_condreg_creqv;
    sc_out<bool> o_condreg_crandc;
    sc_out<bool> o_condreg_crorc;
    sc_out<bool> o_condreg_mcrf;

    void do_identify()
    {
        o_instr_suffix.write(i_instr.read());
        // TODO
    }

    SC_CTOR(Identify)
    {
        SC_METHOD(do_identify);
        // Combinational: sensitive to all inputs
        sensitive << i_clk << i_rst << i_en << i_instr;
        sensitive << i_arb_full_mask;
    }
};
int sc_main(int argc, char* argv[])
{
    sc_signal<bool> rst;
    sc_signal<bool> en;
    sc_signal<sc_bv<32>> instr;
    sc_signal<sc_bv<32>> instr_prefix;
    sc_signal<sc_bv<32>> instr_suffix;
    sc_signal<bool> branch_identified;
    sc_signal<bool> branch_i_form;
    sc_signal<bool> branch_b_form;
    sc_signal<bool> branch_cond_lr;
    sc_signal<bool> branch_cond_ctr;
    sc_signal<bool> branch_cond_tar;
    sc_signal<bool> stall_fetch_arb;
    sc_signal<bool> arb_full_mask;
    sc_signal<bool> condreg_identified;
    sc_signal<bool> condreg_crand;
    sc_signal<bool> condreg_crnand;
    sc_signal<bool> condreg_cror;
    sc_signal<bool> condreg_crxor;
    sc_signal<bool> condreg_crnor;
    sc_signal<bool> condreg_creqv;
    sc_signal<bool> condreg_crandc;
    sc_signal<bool> condreg_crorc;
    sc_signal<bool> condreg_mcrf;

    sc_clock clk(/*Name*/"TestClock", /*Period*/10, /*Unit*/SC_NS,/*Duty*/0.5);

    sc_trace_file *waveform = sc_create_vcd_trace_file("trace"); // write in trace.vcd
    sc_trace(waveform, clk, "i_clk");
    sc_trace(waveform, rst, "i_rst");
    sc_trace(waveform, en, "i_en");
    sc_trace(waveform, instr, "i_instr");
    sc_trace(waveform, instr_prefix, "o_instr_prefix");
    sc_trace(waveform, instr_suffix, "o_instr_suffix");
    sc_trace(waveform, branch_identified, "o_branch_identified");
    sc_trace(waveform, branch_i_form, "o_branch_i_form");
    sc_trace(waveform, branch_b_form, "o_branch_b_form");
    sc_trace(waveform, branch_cond_lr, "o_branch_cond_lr");
    sc_trace(waveform, branch_cond_ctr, "o_branch_cond_ctr");
    sc_trace(waveform, branch_cond_tar, "o_branch_cond_tar");
    sc_trace(waveform, stall_fetch_arb, "o_stall_fetch_arb");
    sc_trace(waveform, arb_full_mask, "i_arb_full_mask");
    sc_trace(waveform, condreg_identified, "o_condreg_identified");
    sc_trace(waveform, condreg_crand, "o_condreg_crand");
    sc_trace(waveform, condreg_crnand, "o_condreg_crnand");
    sc_trace(waveform, condreg_cror, "o_condreg_cror");
    sc_trace(waveform, condreg_crxor, "o_condreg_crxor");
    sc_trace(waveform, condreg_crnor, "o_condreg_crnor");
    sc_trace(waveform, condreg_creqv, "o_condreg_creqv");
    sc_trace(waveform, condreg_crandc, "o_condreg_crandc");
    sc_trace(waveform, condreg_crorc, "o_condreg_crorc");
    sc_trace(waveform, condreg_mcrf, "o_condreg_mcrf");

    Stimulus stim("Stimulus");
    stim.i_clk(clk);
    stim.o_rst(rst);
    stim.o_en(en);
    stim.o_instr(instr);
    stim.o_arb_full_mask(arb_full_mask);

    Identify dut("Identify");
    dut.i_clk(clk);
    dut.i_rst(rst);
    dut.i_en(en);
    dut.i_instr(instr);
    dut.o_instr_prefix(instr_prefix);
    dut.o_instr_suffix(instr_suffix);
    dut.o_branch_identified(branch_identified);
    dut.o_branch_i_form(branch_i_form);
    dut.o_branch_b_form(branch_b_form);
    dut.o_branch_cond_lr(branch_cond_lr);
    dut.o_branch_cond_ctr(branch_cond_ctr);
    dut.o_branch_cond_tar(branch_cond_tar);
    dut.o_stall_fetch_arb(stall_fetch_arb);
    dut.i_arb_full_mask(arb_full_mask);
    dut.o_condreg_identified(condreg_identified);
    dut.o_condreg_crand(condreg_crand);
    dut.o_condreg_crnand(condreg_crnand);
    dut.o_condreg_cror(condreg_cror);
    dut.o_condreg_crxor(condreg_crxor);
    dut.o_condreg_crnor(condreg_crnor);
    dut.o_condreg_creqv(condreg_creqv);
    dut.o_condreg_crandc(condreg_crandc);
    dut.o_condreg_crorc(condreg_crorc);
    dut.o_condreg_mcrf(condreg_mcrf);
    
    Monitor mon("Monitor");
    mon.i_clk(clk);
    mon.i_rst(rst);
    mon.i_en(en);
    mon.i_instr(instr);
    mon.i_arb_full_mask(arb_full_mask);
    mon.i_instr_prefix(instr_prefix);
    mon.i_instr_suffix(instr_suffix);
    mon.i_branch_identified(branch_identified);
    mon.i_branch_i_form(branch_i_form);
    mon.i_branch_b_form(branch_b_form);
    mon.i_branch_cond_lr(branch_cond_lr);
    mon.i_branch_cond_ctr(branch_cond_ctr);
    mon.i_branch_cond_tar(branch_cond_tar);
    mon.i_stall_fetch_arb(stall_fetch_arb);
    mon.i_condreg_identified(condreg_identified);
    mon.i_condreg_crand(condreg_crand);
    mon.i_condreg_crnand(condreg_crnand);
    mon.i_condreg_cror(condreg_cror);
    mon.i_condreg_crxor(condreg_crxor);
    mon.i_condreg_crnor(condreg_crnor);
    mon.i_condreg_creqv(condreg_creqv);
    mon.i_condreg_crandc(condreg_crandc);
    mon.i_condreg_crorc(condreg_crorc);
    mon.i_condreg_mcrf(condreg_mcrf);

    sc_start(); // Runs forever
    //sc_start(10, SC_NS); // run for 10ns
    //sc_stop();
    return 0;

}
