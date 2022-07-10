import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
import cocotb.simulator as simulator

DEBUG = True # Main switch to turn on/off debugging prints

@cocotb.test()
async def test_branch_facility(dut):
    clock = Clock(dut.i_clk, 1, units="ns") # 1ns clock period
    cocotb.fork(clock.start())
    if DEBUG:
        print("[v] clock initialized")
    dut.i_rst.value = 0b1
    dut.i_instr.value = 0x0000000000000000
    dut.o_next_instr_addr.value = 0x0000000000000000
    dut.i_link_register.value = 0x0000000000000000
    dut.i_count_register.value = 0x0000000000000000
    dut.i_condition_register.value = 0x00000000
    dut.i_is_branch.value = 0b0
    dut.i_is_branch_to_link_register.value = 0b0
    dut.i_en.value = 0b0
    dut.i_32b_mode.value = 0b0
    await Timer(200, units="ps") # reset counters
    dut.i_rst.value = 0b0
    await Timer(200, units="ps") # reset counters
    dut.i_en.value = 0b1
    if DEBUG:
        print("[v] Reset sequence done")
    await Timer(200, units="ps") # reset counters

    assert dut.o_next_instr_addr.value == 0, "First address should be 0"

    await RisingEdge(dut.i_clk)

    # TODO test sequential instructions

# TODO Test the effective address arithmetic wraps around 2**64-1 to address 0
# TODO Try a word instruction at address 2**64-4 -> next seq. instr. is
# undefined
# TODO Try a prefixed instructoin at address 2**64-8 -> next seq. instr is
# undefined
# TODO in 32 bits mode the effective address wraps around 2**32-1
# TODO Try a word instruction at address 2**32-4 -> next seq.instr. is
# undefined
# TODO Try a prefixed instruction at address 2**64-8 -> next seq. instr. is
# undefined
