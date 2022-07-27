import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
import utils
DEBUG = True  # Main switch to turn on/off debugging prints

class Tester:
    Coverage = coverage_section (
      # Branch Instructions coverage events
      CoverPoint("dut.o_bru_en", xf = lambda dut : dut.o_bru_en.value.integer, bins = [0, 1]),
      CoverPoint("top.o_bru_i_form", xf = lambda dut : dut.o_bru_i_form.value.integer, bins = [0, 1]),
      CoverPoint("top.o_bru_b_form", xf = lambda dut : dut.o_bru_b_form.value.integer, bins = [0, 1]),
      CoverPoint("top.o_bru_cond_LR", xf = lambda dut : dut.o_bru_cond_LR.value.integer, bins = [0, 1]),
      CoverPoint("top.o_bru_cond_CTR", xf = lambda dut : dut.o_bru_cond_CTR.value.integer, bins = [0, 1]),
      CoverPoint("top.o_bru_cond_TAR", xf = lambda dut : dut.o_bru_cond_TAR.value.integer, bins = [0, 1]),

      # Condition Registers conditional events
      CoverPoint("dut.o_condreg_en", xf = lambda dut : dut.o_condreg_en.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_crand", xf = lambda dut : dut.o_condreg_crand.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_crnand", xf = lambda dut : dut.o_condreg_crnand.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_cror", xf = lambda dut : dut.o_condreg_cror.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_crxor", xf = lambda dut : dut.o_condreg_crxor.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_crnor", xf = lambda dut : dut.o_condreg_crnor.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_creqv", xf = lambda dut : dut.o_condreg_creqv.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_crandc", xf = lambda dut : dut.o_condreg_crandc.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_crorc", xf = lambda dut : dut.o_condreg_crorc.value.integer, bins = list(range(0,2)) ),
      CoverPoint("dut.o_condreg_mcrf", xf = lambda dut : dut.o_condreg_mcrf.value.integer, bins = list(range(0,2)) ),

      CoverCross("dut.cross", items = ["dut.o_condreg_en", "dut.o_bru_en"])
    )

    @cocotb.coroutine
    @Coverage
    async def coverage_sample(dut):
        """ Doing nothing, just update the coverage """
        pass

    @cocotb.coroutine
    async def _reset_sequence(dut):
        # TODO update for this module
        dut.i_rst.value = 0b1
        dut.i_32b_mode.value = 0b0
        dut.i_en.value = 0b0
        dut.i_stall.value = 0b0
        dut.i_instr_prefix.value = 0x0000000000000000
        dut.i_instr_suffix.value = 0x0000000000000000
        dut.i_is_op34.value = 0b0
        dut.i_cia.value =0x0000000000000000

    def _init_expected(self):
        self.o_cr = None
        self.o_rf_addr = None
        self.o_rf_enr = None
        self.o_rf_enw = None
        self.o_data_addr = None
        self.o_data_enr = None
        self.o_data_enw = None
        self.err_invalid_load_instr = None
        self.o_stall = None
        self.cia = 0

    @cocotb.coroutine
    async def _assert_expected(self, dut):
        assert dut.o_cr.value.integer == self.o_cr
        assert dut.o_rf_addr == self.o_rf_addr
        assert dut.o_rf_enr == self.o_rf_enr
        assert dut.o_rf_enw == self.o_rf_enw
        assert dut.o_data_addr == self.o_data_addr
        assert dut.o_data_enr == self.o_data_enr
        assert dut.o_data_enw == self.o_data_enw
        # PLBZ: if R is equal to 1 and RA is not equal to 0, the instruction form if invalid
        assert dut.err_invalid_load_instr == self.err_invalid_load_instr
        assert dut.o_stall == self.o_stall

    def _print_expected_vs_dut(self, dut):
        if not DEBUG:
            return # Disable all prints if not in debug mode
        print(f"DUT's CR:   0b{dut.o_cr.value.integer:>032b}")

    def _generate_random_inputs(self, dut):
        dut.i_rst.value = 0b0 # TODO reset at random
        dut.i_32b_mode.value = 0b0 # TODO test 32b mode
        dut.i_en.value = 0b1 # TODO set at random
        dut.i_stall.value = 0b0 # TODO set at random

        dut.i_instr_prefix.value = 0x0000000000000000
        dut.i_instr_suffix.value = 0x0000000000000000
        dut.i_is_op34.value = 0b0
        dut.i_cia.value =0x0000000000000000

        bt = random.randint(0, 2**5-1)
        ba = random.randint(0, 2**5-1)
        bb = random.randint(0, 2**5-1)
        instr = int(utils.condreg_xl_form_to_string(PO=19, BT=bt, BA=ba, BB=bb, XO=xo)[:32], 2)
        dut.i_instr.value = instr
        dut.i_en.value = 0b1
        dut.i_crand.value = is_crand(xo)
        dut.i_crnand.value = is_crnand(xo)
        dut.i_cror.value = is_cror(xo)
        dut.i_crxor.value = is_crxor(xo)
        dut.i_crnor.value = is_crnor(xo)
        dut.i_creqv.value = is_creqv(xo)
        dut.i_crandc.value = is_crandc(xo)
        dut.i_crorc.value = is_crorc(xo)
        dut.i_mcrf.value = is_mcrf(xo)
        bf = utils.select_bits(reg=instr, size=32, from_=6, to=8)
        bfa = utils.select_bits(reg=instr, size=32, from_=11, to=13)

    def _update_expected(self):
        CR = expected_CR(oldcr=CR, xo=xo, bt=bt, ba=ba, bb=bb, bf=bf, bfa=bfa)

    @cocotb.test()
    async def test_loadstoreunit(self, dut):
        """ Test Fixed point load and stores """
        # Initialization sequence
        clock = Clock(dut.i_clk, 1, units="ns")  # 1ns clock period
        cocotb.fork(clock.start())

        await _reset_sequence(dut)
        self._init_expected()

        #output logic [0:31] o_cr // Condition Register (CR)
        #await Timer(200, units="ps")  # reset counters
        for i in range(1000):
            await RisingEdge(dut.i_clk)
            await Timer(200, units="ps")

            await coverage_sample(dut)

            self._print_expected_vs_dut(dut)

            await self._assert_expected(dut)

            self._generate_random_inputs(dut)

            self._update_expected()

    if __name__ == '__main__':
        import doctest
        doctest.testmod()
