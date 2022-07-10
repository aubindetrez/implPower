import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
import cocotb.simulator as simulator

DEBUG = True # Main switch to turn on/off debugging prints

@cocotb.test()
async def test_identify(dut):
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

    # TODO identify branch instructions

    # TODO identify other instructions

    dut.i_instr = 0x0000000000000020
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_prefixed.value == 1, "This is a prefixed instruction"

    dut.i_instr = 0x0000000000000000
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_prefixed.value == 0, "This is not a prefixed instruction"

# TODO Test this: (Section 1.10.2 - Big-Endian example)
# address 00 -> 00 01 02 03 cmplwi r5, 0
# address 04 -> 04 05 06 07 beq done
# address 08 -> 08 09 0A 0B lwzux r4, r5, r6
# address 0C -> 0C 0D 0E 0F add r7, r7, r7
# address 10 -> 10 11 12 13 "some prefix"
# address 14 -> 14 15 16 17 "some suffix"
# address 18 -> 18 19 1A 1B subi r5, r5, 4
