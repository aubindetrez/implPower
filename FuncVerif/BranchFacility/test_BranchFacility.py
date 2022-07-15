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

def select_bit(reg: int, size: int, bit:int) -> int:
    """
    >>> select_bit(0b0100, 4, 1)
    1
    >>> select_bit(0b0100, 4, 0)
    0
    >>> select_bit(0b0100, 4, 2)
    0
    """
    fmt="{:0"+str(size)+"b}"
    s = fmt.format(reg)
    return int(s[bit])

def adds_64b(a: int, b: int) -> int:
    """
    >>> adds_64b(2**64-1, 1)
    0
    >>> adds_64b(374, 698)
    1072
    """
    ua = numpy.uint64(a)
    ub = numpy.uint64(b)
    return int(ua+ub)

def sub_64b(a: int, b: int) -> numpy.uint64:
    """
    >>> sub_64b(1, 2)
    18446744073709551615
    >>> sub_64b(2**64-1, -1)
    0
    """
    ua = numpy.uint64(a)
    ub = numpy.uint64(b)
    return numpy.uint64(ua-ub)

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
    dut.i_instr.value = int(utils.branch_i_form_to_string(PO=18, LI=LI, AA=1, LK=1)[:32], 2)
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
    assert dut.o_next_instr_addr.value.integer == expected_branch_target_addr, """According to
    ISA section 2.4 if LK=1 and AA=1 then NIA = sign_extended(LI << 2)
    """
    await RisingEdge(dut.i_clk) # Icache will load data from address o_next_instr_addr (NIA)
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction
    assert dut.cia.value.integer == expected_branch_target_addr, """Internal signal CIA should
    take the value from NIA"""
    print("JUMP worked")

    # Check if the link register has been updated by last instruction
    assert dut.o_link_register.value.integer == 8, """See ISA section 2.4, if
    LK=1 then the effective address of the instruction folloging the branch
    instruction is placed on the Link register"""

    # The Identify unit returns a Branch I-form instruction with AA=0 and LK=0
    # And a negative LI
    LI = 0x800FEE
    dut.i_instr.value = int(utils.branch_i_form_to_string(PO=18, LI=LI, AA=0, LK=0)[:32], 2)
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
    assert dut.o_next_instr_addr.value.integer == expected_branch_target_addr, """According to
    ISA section 2.4 if AA=0 then NIA = CIA + sign_extended(LI << 2)
    """
    await RisingEdge(dut.i_clk) # Icache will load data from address o_next_instr_addr (NIA)
    await Timer(200, units="ps") # Give some time to the Icache to return an instruction
    assert dut.cia.value.integer == expected_branch_target_addr, """Internal signal CIA should
    take the value from NIA"""
    print("JUMP worked")

    # Check if the last instruction didn't update the Link Register (LR)
    assert dut.o_link_register.value.integer == 8, """See ISA section 2.4, this
    instruction should not update the Link Register (LK=0)
    """

@cocotb.test()
async def test_bf_64b_branch_b(dut):
    """ Test branch facility for Branch Conditional B-form / 64bit mode """
    await init_sequence(dut, mode=64)
    NIA = 0
    CIA = 0 # Registers are expected to be reset
    LR = 0 # Registers are expected to be reset
    CTR = 0 # Registers are expected to be reset
    assert dut.o_next_instr_addr.value.integer == NIA, "First address should be 0"


    for iteration in range(10):
        await RisingEdge(dut.i_clk) # Icache load the data at NIA (Next Instruction Address)
        print("Fake Cache is loading address 0x{:x}".format(NIA))
        CIA = NIA
        await Timer(200, units="ps") # Give some time to the Icache to return an instruction
        assert dut.cia.value.integer == CIA, """Internal signal CIA should take the value from NIA"""
        print("JUMP worked")
        assert dut.o_link_register.value.integer == LR, """Link Register (LK=0) is wrong, See ISA section 2.4"""
        # TODO FIXME important: create o_count_register instead of i_count_register and check it
        assert dut.o_count_register.value.integer == CTR

        # Parameters for this iteration
        A = utils.random_bit()
        T = utils.random_bit()
        tB0 = random.randint(0, 7)
        BI = random.randint(0, 2**5-1)
        if tB0 == 0: BO=random_bin("0000?")  # Decrement CTR then branch if CTR[M:63] != 0 and CR[BI] == 0
        elif tB0 == 1: BO=random_bin("0001?")  # Decrement the CTR then branch if CTR[M:63] == 0 and CR[BI] == 0
        elif tB0 == 2: BO=0b00100 | A << 1 | T # Branch if CR[BI] == 0
        elif tB0 == 3: BO=random_bin("0100?")  # Decrement the CTR, then branch if CTR[M:63] != 0 and CR[BI] == 1
        elif tB0 == 4: BO=random_bin("0101?")  # Decrement the CTR, then branch if CTR[M:63] == 0 and CR[BI] == 1
        elif tB0 == 5: BO=0b01100 | A << 1 | T # Branch if CR[BI] == 1
        elif tB0 == 6: BO=0b10000 | A << 3 | T # Decrement the CTR, then branch if CTR[M:63] != 0
        elif tB0 == 7: BO=0b10010 | A << 3 | T # Decrement the CTR, then branch if CTR[M:63] == 0
        else: BO=random_bin("1?1??")  # Branch always

        LK = utils.random_bit()
        AA = utils.random_bit()
        CR = utils.random_32b() # Conditional Register, see Section 2.3.1 -> CR[32:63]
        BD = random.randint(0, 2**14-1)
        exts_BD = utils.exts(BD << 2, length=14, new_length=64) # See ISA section 2.4
        # Update expected LR
        if LK == 1:
            LR = CIA+4 # Effective address of the instruction following the Branch Instruction
        # Update expected CTR
        if tB0 == 0:   sub_64b(CTR, 1)
        elif tB0 == 1: sub_64b(CTR, 1)
        elif tB0 == 2: pass
        elif tB0 == 3: sub_64b(CTR, 1)
        elif tB0 == 4: sub_64b(CTR, 1)
        elif tB0 == 5: pass
        elif tB0 == 6: sub_64b(CTR, 1)
        elif tB0 == 7: sub_64b(CTR, 1)
        else:          pass

        # Update the expected Next Instruction Address (NIA)
        going_to_branch = False # TODO
        if AA == 0:
            effective_address = adds_64b(CIA, exts_BD)
        else:
            effective_address = exts_BD
        if tB0 == 0:   going_to_branch = select_bit(reg=CR, size=32, bit=BI) == 0 and CTR != 0 # CTR[0:63]
        elif tB0 == 1: going_to_branch = select_bit(reg=CR, size=32, bit=BI) == 0 and CTR == 0
        elif tB0 == 2: going_to_branch = select_bit(reg=CR, size=32, bit=BI) == 0
        elif tB0 == 3: going_to_branch = select_bit(reg=CR, size=32, bit=BI) == 1 and CTR != 0
        elif tB0 == 4: going_to_branch = select_bit(reg=CR, size=32, bit=BI) == 1 and CTR == 0
        elif tB0 == 5: going_to_branch = select_bit(reg=CR, size=32, bit=BI) == 1
        elif tB0 == 6: going_to_branch = CTR != 0
        elif tB0 == 7: going_to_branch = CTR == 0
        else:          going_to_branch = True
        if going_to_branch:
            NIA = effective_address


        # Print information about the current iteration for debugging purpose
        if DEBUG == True:
            pass # TODO

        dut.i_instr.value = int(utils.branch_b_form_to_string(16, BO, BI, BD, AA, LK)[:32], 2)
        dut.i_stall.value = 0b0 # No stall
        dut.i_en.value = 0b1 # This is a branch
        dut.i_i_form.value = 0b0
        dut.i_b_form.value = 0b1 # Branch conditional B-form like described in Section 2.4
        dut.i_cond_LR.value = 0b0
        dut.i_cond_CTR.value = 0b0
        dut.i_cond_TAR.value = 0b0
        dut.i_condition_register.value = CR
        dut.i_target_address_register.value = utils.random_64b()
        # dut.i_count_register.value = CTR # TODO delete this signal in the design
        await Timer(100, units="ps") # Give time for the combinatinal logic
        assert dut.o_next_instr_addr.value.integer == NIA, "NIA should be {}".format(NIA)

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
if __name__ == "__main__":
    import doctest
    doctest.testmod()
