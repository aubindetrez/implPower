import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
import utils
import common
DEBUG = False  # Main switch to turn on/off debugging prints


@cocotb.test()
async def test_bf_64b_bctar(dut):
    """ Test branch facility for Branch Conditional to Branch Target Address Register XL-form
    / 64bit mode (mnemonic bctar[l])
    Specification in the Open Power ISA 2.4
    """
    await common.init_sequence(dut, mode=64)
    # Initialize registers modified by the Device Under Test (DUT)
    NIA = 0
    CIA = 0  # Registers are expected to be reset
    LR = 0  # Registers are expected to be reset
    CTR = 0  # Registers are expected to be reset
    TAR = 0
    assert dut.o_next_instr_addr.value.integer == NIA, "First address after reset sequence should be 0"

    for iteration in range(100):
        # Icache load the data at NIA (Next Instruction Address)
        await RisingEdge(dut.i_clk)
        if DEBUG:
            print("Fake Cache is loading address 0x{:x}".format(NIA))
        CIA = NIA
        # Give some time for the I-cache to return an instruction
        await Timer(200, units="ps")
        assert dut.cia.value.integer == CIA, """Internal signal CIA should take
                                                            the value from NIA"""
        if DEBUG:
            print("JUMP worked")
        assert dut.o_link_register.value.integer == LR, f"{dut.o_link_register.value.integer} != {LR}"
        # Should not be modified
        assert dut.o_count_register.value.integer == CTR, f"{dut.o_count_register.value.integer} != {CTR}"

        # Conditional Register, see Section 2.3.1 -> CR[32:63]
        TAR = utils.random_64b()
        CR = utils.random_32b()
        A = utils.random_bit()
        T = utils.random_bit()
        LK = utils.random_bit()
        BI = random.randint(0, 2**5-1)
        # BH: Target address prediction, See Power ISA Section 2.4 Figure 42
        BH = random.randint(0, 3)
        tBO = random.randint(0, 7)  # Type for BO
        BO = common.generate_BO(tBO=tBO, A=A, T=T)
        LR = expected_LR(LR=LR, CIA=CIA, LK=LK)
        CTR = expected_CTR(CTR=CTR, tBO=tBO)
        going_to_branch = False
        if common.should_branch(tBO=tBO, CR=CR, BI=BI, CTR=CTR):
            going_to_branch = True
            NIA = expected_branch_target_address(TAR=TAR)
        else:
            NIA = CIA + 4

        # Print information about the current iteration for debugging purpose
        if DEBUG == True:
            print("Sending XL-form Conditional Branch to Count Register:")
            print(f"\tCIA = 0x{CIA:>x} = 0b{CIA:>064b}")
            print(f"\tCR = 0x{CR:>x} = 0b{CR:>032b}")
            print("\tOP = 19 = 0b010011 (Branch conditional to Link Register XL-form)")
            print(
                f"\tBO = 0x{BO:>x} = 0b{BO:>05b} (type: {tBO} - {common.str_tBO(tBO)})")
            print(f"\tBI = {BI} = 0x{BI:>x} = 0b{BI:>05b}")
            print(f"\tBD = 0x{BH:>x} = 0b{BH:>014b} "
                  f"({common.str_BH(BH,'bclr')})")
            print(f"\tLK = {LK}")
            print(f"Expected to branch: {going_to_branch}")
            print(f"Expected NIA: 0x{NIA:>x} = 0b{NIA:>064b}")
            print(f"Expected LR: 0x{LR:>x} = 0b{LR:>064b}")
            print(f"Expected CTR: 0x{CTR:>x} = 0b{CTR:>064b}")

        dut.i_instr.value = int(utils.branch_xl_form_to_string(
            PO=19, BO=BO, BI=BI, BH=BH, XO=560, LK=LK)[:32], 2)
        dut.i_stall.value = 0b0  # No stall
        dut.i_en.value = 0b1  # This is a branch
        dut.i_i_form.value = 0b0
        dut.i_b_form.value = 0b0
        dut.i_cond_LR.value = 0b0
        # Branch conditional to Count Register XL-form like described in Section 2.4
        dut.i_cond_CTR.value = 0b0
        dut.i_cond_TAR.value = 0b1
        dut.i_condition_register.value = CR
        dut.i_target_address_register.value = TAR
        await Timer(100, units="ps")  # Give time for the combinatinal logic
        assert dut.o_next_instr_addr.value.integer == NIA, f"NIA should be {NIA:>x} not {dut.o_next_instr_addr.value.integer:>x}"
        assert dut.dbg_invalid_instruction == 0


def expected_branch_target_address(TAR: int) -> int:
    return TAR & 0xfffffffffffffffc


def expected_LR(LR, CIA, LK):
    if LK == 1:
        return CIA+4  # Effective address of the instruction following the Branch Instruction
    return LR


def expected_CTR(CTR, tBO) -> int:
    # Returns new CTR value
    if tBO == 0:
        return utils.sub_64b(CTR, 1)
    elif tBO == 1:
        return utils.sub_64b(CTR, 1)
    elif tBO == 2:
        return CTR
    elif tBO == 3:
        return utils.sub_64b(CTR, 1)
    elif tBO == 4:
        return utils.sub_64b(CTR, 1)
    elif tBO == 5:
        return CTR
    elif tBO == 6:
        return utils.sub_64b(CTR, 1)
    elif tBO == 7:
        return utils.sub_64b(CTR, 1)
    else:
        return CTR
