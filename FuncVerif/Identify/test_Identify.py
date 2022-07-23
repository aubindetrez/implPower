import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
from cocotb_coverage.coverage import *
import cocotb.simulator as simulator
import utils

DEBUG = True  # Main switch to turn on/off debugging prints


async def init_sequence(dut):
    clock = Clock(dut.i_clk, 1, units="ns")  # 1ns clock period
    cocotb.fork(clock.start())
    if DEBUG:
        print("[v] clock initialized")
    dut.i_rst.value = 0b1
    dut.i_en.value = 0b0
    dut.i_instr.value = 0x0000000000000000
    await Timer(200, units="ps")  # reset counters
    dut.i_rst.value = 0b0
    await Timer(200, units="ps")  # reset counters
    dut.i_en.value = 0b1
    if DEBUG:
        print("[v] Reset sequence done")
    await Timer(200, units="ps")  # reset counters

ID_Coverage = coverage_section (
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
@ID_Coverage
async def coverage_sample(dut):
    """ Doing nothing, just update the coverage """
    pass


@cocotb.test()
async def test_identify_prefixed(dut):
    await init_sequence(dut)

    dut.i_instr = 0x0400000000000000
    await RisingEdge(dut.i_clk)
    assert dut.is_prefixed.value == 1, "This is a prefixed instruction"

    dut.i_instr = 0x0000000000000000
    await RisingEdge(dut.i_clk)
    assert dut.is_prefixed.value == 0, "This is not a prefixed instruction"

@cocotb.test()
async def test_identify_branch(dut):
    log = cocotb.logging.getLogger("cocotb.log")

    await init_sequence(dut)
    await coverage_sample(dut)

    # Power ISA Section 2.4
    dut.i_instr = int(utils.branch_i_form_to_string(
        PO=18, LI=0xcafe, AA=1, LK=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_instr.value.binstr == '01001000000000110010101111111011', "Instruction do not match"
    assert dut.o_bru_en.value == 1, "That instruction must be decoded by the BranchUnit"
    assert dut.o_bru_i_form.value == 1, "This is an I form branch"
    assert dut.o_bru_b_form.value == 0, "This isn't a B form branch but an I form branch"
    assert dut.o_bru_cond_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.o_bru_cond_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.o_bru_cond_TAR.value == 0, "This is not a conditional branch to TAR"
    assert dut.o_condreg_en.value == 0
    await coverage_sample(dut)

    dut.i_instr = int(utils.branch_b_form_to_string(
        PO=16, BO=18, BI=27, BD=0xafe, AA=1, LK=0), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 1
    assert dut.o_bru_instr.value.binstr == '01000010010110110010101111111010', "Instruction do not match"
    assert dut.o_bru_i_form.value == 0, "This is not an I form branch but a B form branch"
    assert dut.o_bru_b_form.value == 1, "This is a B form branch"
    assert dut.o_bru_cond_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.o_bru_cond_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.o_bru_cond_TAR.value == 0, "This is not a conditional branch to TAR"
    assert dut.o_condreg_en.value == 0
    await coverage_sample(dut)

    dut.i_instr = int(utils.branch_xl_form_to_string(
        PO=19, BO=7, BI=4, BH=0b10, XO=16, LK=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 1
    assert dut.o_bru_instr.value.binstr == '01001100111001000001000000100001', "Instruction do not match"
    assert dut.o_bru_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.o_bru_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.o_bru_cond_LR.value == 1, "This is a conditional branch to LR"
    assert dut.o_bru_cond_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.o_bru_cond_TAR.value == 0, "This is not a conditional branch to TAR"
    assert dut.o_condreg_en.value == 0
    await coverage_sample(dut)

    dut.i_instr = int(utils.branch_xl_form_to_string(
        PO=19, BO=7, BI=4, BH=0b10, XO=528, LK=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 1
    assert dut.o_bru_instr.value.binstr == '01001100111001000001010000100001', "Instruction do not match"
    assert dut.o_bru_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.o_bru_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.o_bru_cond_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.o_bru_cond_CTR.value == 1, "This is a conditional branch to CTR"
    assert dut.o_bru_cond_TAR.value == 0, "This is not a conditional branch to TAR"
    assert dut.o_condreg_en.value == 0
    await coverage_sample(dut)

    dut.i_instr = int(utils.branch_xl_form_to_string(
        PO=19, BO=7, BI=4, BH=0b10, XO=560, LK=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 1
    assert dut.o_bru_instr.value.binstr == '01001100111001000001010001100001', "Instruction do not match"
    assert dut.o_bru_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.o_bru_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.o_bru_cond_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.o_bru_cond_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.o_bru_cond_TAR.value == 1, "This is a conditional branch to TAR"
    assert dut.o_condreg_en.value == 0
    await coverage_sample(dut)

    # Power ISA section 2.5.1
    # CRAND Instruction: Condition register AND XL-form
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=257), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 1
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # CRNAND
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=225), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 1
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # CROR
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=449), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 1
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # CRXOR
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=193), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 1
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # CRNOR
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=33), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 1
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # CREQV
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=289), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 1
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # CRANDC
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=129), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 1
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # CRORC
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=417), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 1
    assert dut.o_condreg_mcrf.value == 0
    await coverage_sample(dut)

    # MCRF
    dut.i_instr = int(utils.condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6,
        XO=0), 2)
    await RisingEdge(dut.i_clk)
    assert dut.o_bru_en.value == 0
    assert dut.o_condreg_en.value == 1
    assert dut.o_condreg_crand.value == 0
    assert dut.o_condreg_crnand.value == 0
    assert dut.o_condreg_cror.value == 0
    assert dut.o_condreg_crxor.value == 0
    assert dut.o_condreg_crnor.value == 0
    assert dut.o_condreg_creqv.value == 0
    assert dut.o_condreg_crandc.value == 0
    assert dut.o_condreg_crorc.value == 0
    assert dut.o_condreg_mcrf.value == 1
    await coverage_sample(dut)

    coverage_db.report_coverage(log.info, bins=True)
