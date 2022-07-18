import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
import utils
import common
DEBUG = False  # Main switch to turn on/off debugging prints


@cocotb.test()
async def test_bf_64b_branh_i(dut):
    """ Test branch facility for Branch I-form / 64bit mode """
    await common.init_sequence(dut, mode=64)
    assert dut.o_next_instr_addr.value.integer == 0, "First address should be 0"

    await RisingEdge(dut.i_clk)  # Icache load data from address 0
    # Give some time to the Icache to return an instruction
    await Timer(200, units="ps")

    # The Identify unit do not return a Branch -> Sequential instruction
    dut.i_instr.value = utils.random_32b()
    dut.i_stall.value = 0b0  # No stall
    dut.i_en.value = 0b0  # This is not a branch
    dut.i_i_form.value = utils.random_bit()
    dut.i_b_form.value = utils.random_bit()
    dut.i_cond_LR.value = utils.random_bit()
    dut.i_cond_CTR.value = utils.random_bit()
    dut.i_cond_TAR.value = utils.random_bit()
    dut.i_condition_register.value = utils.random_32b()
    dut.i_target_address_register.value = utils.random_64b()
    await Timer(100, units="ps")  # Give time for the combinatinal logic
    assert dut.o_next_instr_addr.value.integer == 4, """If it is not stalling, this is
    a sequential instruction (no branch), the NIA should be CIA+4"""

    # Icache will load data from address o_next_instr_addr (NIA)
    await RisingEdge(dut.i_clk)
    # Give some time to the Icache to return an instruction
    await Timer(200, units="ps")

    # The Identify unit returns a Branch I-form instruction with AA=1 and LK=1
    LI = 0xCAFE
    dut.i_instr.value = int(utils.branch_i_form_to_string(
        PO=18, LI=LI, AA=1, LK=1)[:32], 2)
    expected_branch_target_addr = utils.exts(LI << 2, length=26, new_length=64)
    if DEBUG:
        print("Sending JUMP to address: "+str(expected_branch_target_addr))
    dut.i_stall.value = 0b0  # No stall
    dut.i_en.value = 0b1  # This is a branch
    dut.i_i_form.value = 0b1
    dut.i_b_form.value = 0b0
    dut.i_cond_LR.value = 0b0
    dut.i_cond_CTR.value = 0b0
    dut.i_cond_TAR.value = 0b0
    dut.i_condition_register.value = utils.random_32b()
    dut.i_target_address_register.value = utils.random_64b()
    await Timer(100, units="ps")  # Give time for the combinatinal logic
    assert dut.o_next_instr_addr.value.integer == expected_branch_target_addr, """According to
    ISA section 2.4 if LK=1 and AA=1 then NIA = sign_extended(LI << 2)
    """
    await RisingEdge(dut.i_clk)  # Icache will load data from address o_next_instr_addr (NIA)
    # Give some time to the Icache to return an instruction
    await Timer(200, units="ps")
    assert dut.cia.value.integer == expected_branch_target_addr, """Internal signal CIA should
    take the value from NIA"""
    if DEBUG:
        print("JUMP worked")

    # Check if the link register has been updated by last instruction
    assert dut.o_link_register.value.integer == 8, """See ISA section 2.4, if
    LK=1 then the effective address of the instruction folloging the branch
    instruction is placed on the Link register"""

    # The Identify unit returns a Branch I-form instruction with AA=0 and LK=0
    # And a negative LI
    LI = 0x800FEE
    dut.i_instr.value = int(utils.branch_i_form_to_string(
        PO=18, LI=LI, AA=0, LK=0)[:32], 2)
    # See ISA section 2.4
    exts_li = utils.exts(LI << 2, length=26, new_length=64)
    expected_branch_target_addr = utils.adds_64b(
        expected_branch_target_addr, exts_li)  # 64b addition
    if DEBUG:
        print("Sending JUMP to address (CIA+LI): " +
              str(expected_branch_target_addr))
    dut.i_stall.value = 0b0  # No stall
    dut.i_en.value = 0b1  # This is a branch
    dut.i_i_form.value = 0b1
    dut.i_b_form.value = 0b0
    dut.i_cond_LR.value = 0b0
    dut.i_cond_CTR.value = 0b0
    dut.i_cond_TAR.value = 0b0
    dut.i_condition_register.value = utils.random_32b()
    dut.i_target_address_register.value = utils.random_64b()
    await Timer(100, units="ps")  # Give time for the combinatinal logic
    if DEBUG:
        print("Address returned by the device under test: " +
              str(dut.o_next_instr_addr.value.integer))
    assert dut.o_next_instr_addr.value.integer == expected_branch_target_addr, """According to
    ISA section 2.4 if AA=0 then NIA = CIA + sign_extended(LI << 2)
    """
    await RisingEdge(dut.i_clk)  # Icache will load data from address o_next_instr_addr (NIA)
    # Give some time to the Icache to return an instruction
    await Timer(200, units="ps")
    assert dut.cia.value.integer == expected_branch_target_addr, """Internal signal CIA should
    take the value from NIA"""
    if DEBUG:
        print("JUMP worked")

    # Check if the last instruction didn't update the Link Register (LR)
    assert dut.o_link_register.value.integer == 8, """See ISA section 2.4, this
    instruction should not update the Link Register (LK=0)
    """
