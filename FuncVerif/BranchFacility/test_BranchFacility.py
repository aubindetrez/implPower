import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
import cocotb.simulator as simulator
import utils

DEBUG = True # Main switch to turn on/off debugging prints

async def init_sequence(dut, mode):
    clock = Clock(dut.i_clk, 1, units="ns") # 1ns clock period
    cocotb.fork(clock.start())
    if DEBUG:
        print("[v] clock initialized")
    dut.i_rst.value = 0b1
    if mode == 32:
        dut.i_32b_mode.value = 0b1 # 32b mode
    elif mode == 64:
        dut.i_32b_mode.value = 0b0 # 64b mode
    else:
        print("Error: init_sequence, {} mode does not exist".format(mode))
        exit(1)
    dut.i_stall.value = 0b0

    dut.i_instr.value = 0x0000000000000000
    dut.i_en.value = 0b0
    dut.i_i_form.value = 0b0
    dut.i_b_form.value = 0b0
    dut.i_cond_LR.value = 0b0
    dut.i_cond_CTR.value = 0b0
    dut.i_cond_TAR.value = 0b0

    dut.i_condition_register.value = 0x00000000
    dut.i_target_address_register.value = 0x0000000000000000
    dut.i_count_register.value = 0x0000000000000000

    await Timer(200, units="ps") # reset counters
    dut.i_rst.value = 0b0
    await Timer(200, units="ps") # reset counters
    if DEBUG:
        print("[v] Reset sequence done")
    await Timer(200, units="ps") # reset counters

@cocotb.test()
async def test_bf_64b_branh_i(dut):
    """ Test branch facility for Branch I-form / 64bit mode """
    await init_sequence(dut, mode=64)
    assert dut.o_next_instr_addr.value.integer == 0, "First address should be 0"

    await RisingEdge(dut.i_clk) # Icache load data from address 0
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction

    # The Identify unit do not return a Branch -> Sequential instruction
    dut.i_instr.value = utils.random_32b()
    dut.i_stall.value = 0b0 # No stall
    dut.i_en.value = 0b0 # This is not a branch
    dut.i_i_form.value = utils.random_bit()
    dut.i_b_form.value = utils.random_bit()
    dut.i_cond_LR.value = utils.random_bit()
    dut.i_cond_CTR.value = utils.random_bit()
    dut.i_cond_TAR.value = utils.random_bit()
    dut.i_condition_register.value = utils.random_32b()
    dut.i_target_address_register.value = utils.random_64b()
    dut.i_count_register.value = utils.random_64b()
    await Timer(100, units="ps") # Give time for the combinatinal logic
    assert dut.o_next_instr_addr.value.integer == 4, """If it is not stalling, this is
    a sequential instruction (no branch), the NIA should be CIA+4"""

    await RisingEdge(dut.i_clk) # Icache will load data from address o_next_instr_addr (NIA)
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction

    # The Identify unit returns a Branch I-form instruction with AA=1 and LK=1
    LI = 0xCAFE
    #LI = 0x80CAFE # TODO Test this negative LI
    dut.i_instr.value = int(utils.branch_i_form_to_string(PO=18, LI=LI, AA=1, LK=1), 2)
    expected_branch_target_addr = utils.exts(LI << 2, length=26, new_length=64)
    dut.i_stall.value = 0b0 # No stall
    dut.i_en.value = 0b1 # This is a branch
    dut.i_i_form.value = 0b1
    dut.i_b_form.value = 0b0
    dut.i_cond_LR.value = 0b0
    dut.i_cond_CTR.value = 0b0
    dut.i_cond_TAR.value = 0b0
    dut.i_condition_register.value = utils.random_32b()
    dut.i_target_address_register.value = utils.random_64b()
    dut.i_count_register.value = utils.random_64b()
    await Timer(100, units="ps") # Give time for the combinatinal logic
    # The LI field is 30-6 = 24 bits
    # When concatenated with 0b00 it becomes 24+2=26 bits
    # Therefore the sign extention must look for the sign bit at offset 26
    assert dut.o_next_instr_addr.value.integer == utils.BE(expected_branch_target_addr, 64), """According to
    ISA section 2.4 if LK=1 and AA=1 then NIA = sign_extended(LI << 2)
    """
    await RisingEdge(dut.i_clk) # Icache will load data from address o_next_instr_addr (NIA)
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction

    # Check if the link register has been updated by last instruction
    assert dut.o_link_register.value.integer == 8, """See ISA section 2.4, if
    LK=1 then the effective address of the instruction folloging the branch
    instruction is placed on the Link register"""


    # TODO The Identify unit returns a Branch I-form instruction with AA=0 and LK=1

    # TODO The Identify unit returns a Branch I-form instruction with AA=1 and LK=0

    # TODO Test stall

# TODO Test address wrap around 2**64-1 to address 0
# TODO Try a word instruction at address 2**64-4 -> next seq. instr. is
# undefined
# TODO Try a prefixed instructoin at address 2**64-8 -> next seq. instr is
# undefined

# TODO in 32 bits mode the effective address wraps around 2**32-1
# TODO Try a word instruction at address 2**32-4 -> next seq.instr. is
# undefined
# TODO Try a prefixed instruction at address 2**64-8 -> next seq. instr. is
# undefined

# TODO test err_branch_on_stall
