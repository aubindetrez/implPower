import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
import cocotb.simulator as simulator
import utils

DEBUG = True # Main switch to turn on/off debugging prints

async def init_sequence(dut):
    clock = Clock(dut.i_clk, 1, units="ns") # 1ns clock period
    cocotb.fork(clock.start())
    if DEBUG:
        print("[v] clock initialized")
    dut.i_rst.value = 0b1
    dut.i_en.value = 0b0
    dut.i_instr.value = 0x0000000000000000
    await Timer(200, units="ps") # reset counters
    dut.i_rst.value = 0b0
    await Timer(200, units="ps") # reset counters
    dut.i_en.value = 0b1
    if DEBUG:
        print("[v] Reset sequence done")
    await Timer(200, units="ps") # reset counters

@cocotb.test()
async def test_identify_prefixed(dut):
    await init_sequence(dut)

    dut.i_instr = 0x0000000000000020
    await RisingEdge(dut.i_clk)
    assert dut.is_prefixed.value == 1, "This is a prefixed instruction"

    dut.i_instr = 0x0000000000000000
    await RisingEdge(dut.i_clk)
    assert dut.is_prefixed.value == 0, "This is not a prefixed instruction"

@cocotb.test()
async def test_identify_branch(dut):
    await init_sequence(dut)
    # Power ISA Section 2.4
    dut.i_instr = int(utils.branch_i_form_to_string(PO=18, LI=0xcafe, AA=1, LK=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.is_branch_i_form.value == 1, "This is an I form branch"
    assert dut.is_branch_b_form.value == 0, "This isn't a B form branch but an I form branch"
    assert dut.is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(utils.branch_b_form_to_string(PO=16, BO=18, BI=27, BD=0xafe, AA=1, LK=0), 2)
    await RisingEdge(dut.i_clk)
    assert dut.is_branch_i_form.value == 0, "This is not an I form branch but a B form branch"
    assert dut.is_branch_b_form.value == 1, "This is a B form branch"
    assert dut.is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(utils.branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=16, S4=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.is_branch_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.is_branch_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.is_branch_cond_to_LR.value == 1, "This is a conditional branch to LR"
    assert dut.is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(utils.branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=528, S4=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.is_branch_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.is_branch_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.is_branch_cond_to_CTR.value == 1, "This is a conditional branch to CTR"
    assert dut.is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(utils.branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=560, S4=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.is_branch_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.is_branch_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.is_branch_cond_to_TAR.value == 1, "This is a conditional branch to TAR"
