import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
import cocotb.simulator as simulator
import utils
import numpy # For uint64

DEBUG = True # Main switch to turn on/off debugging prints
def adds_64b(a: int, b: int) -> int:
    ua = numpy.uint64(a)
    ub = numpy.uint64(b)
    return int(ua+ub)

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
    assert dut.o_next_instr_addr.value.integer == utils.BE(4, 64), """If it is not stalling, this is
    a sequential instruction (no branch), the NIA should be CIA+4"""

    await RisingEdge(dut.i_clk) # Icache will load data from address o_next_instr_addr (NIA)
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction

    # The Identify unit returns a Branch I-form instruction with AA=1 and LK=1
    LI = 0xCAFE
    dut.i_instr.value = int(utils.branch_i_form_to_string(PO=18, LI=LI, AA=1, LK=1), 2)
    expected_branch_target_addr = utils.exts(LI << 2, length=26, new_length=64)
    print("Sending JUMP to address: "+str(expected_branch_target_addr))
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
    assert dut.o_next_instr_addr.value.integer == utils.BE(expected_branch_target_addr, 64), """According to
    ISA section 2.4 if LK=1 and AA=1 then NIA = sign_extended(LI << 2)
    """
    await RisingEdge(dut.i_clk) # Icache will load data from address o_next_instr_addr (NIA)
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction
    assert dut.cia.value.integer == utils.BE(expected_branch_target_addr, 64), """Internal signal CIA should
    take the value from NIA"""
    print("JUMP worked")

    # Check if the link register has been updated by last instruction
    assert dut.o_link_register.value.integer == utils.BE(8, 64), """See ISA section 2.4, if
    LK=1 then the effective address of the instruction folloging the branch
    instruction is placed on the Link register"""

    # The Identify unit returns a Branch I-form instruction with AA=0 and LK=0
    # And a negative LI
    LI = 0x800FEE
    dut.i_instr.value = int(utils.branch_i_form_to_string(PO=18, LI=LI, AA=0, LK=0), 2)
    exts_li = utils.exts(LI << 2, length=26, new_length=64) # See ISA section 2.4
    expected_branch_target_addr = adds_64b(expected_branch_target_addr, exts_li) # 64b addition
    print("Sending JUMP to address (CIA+LI): "+str(expected_branch_target_addr))
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
    print("Address returned by the device under test: "+str(dut.o_next_instr_addr.value.integer))
    assert dut.o_next_instr_addr.value.integer == utils.BE(expected_branch_target_addr, 64), """According to
    ISA section 2.4 if AA=0 then NIA = CIA + sign_extended(LI << 2)
    """
    await RisingEdge(dut.i_clk) # Icache will load data from address o_next_instr_addr (NIA)
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction
    assert dut.cia.value.integer == utils.BE(expected_branch_target_addr, 64), """Internal signal CIA should
    take the value from NIA"""
    print("JUMP worked")

    # Check if the last instruction didn't update the Link Register (LR)
    assert dut.o_link_register.value.integer == utils.BE(8, 64), """See ISA section 2.4, this
    instruction should not update the Link Register (LK=0)
    """

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
