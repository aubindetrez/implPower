import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
import utils
import common
DEBUG = False  # Main switch to turn on/off debugging prints


@cocotb.test()
async def test_bf_64b_bclr(dut):
    """ Test branch facility for Branch Conditional to Link Register XL-form / 64bit mode (mnemonic bclr[l])"""
    await common.init_sequence(dut, mode=64)

    # Registers Modified by the Model (and Device Under Test (DUT))
    NIA = 0
    CIA = 0  # Registers are expected to be reset
    LR = 0  # Registers are expected to be reset
    CTR = 0  # Registers are expected to be reset

    assert dut.o_next_instr_addr.value.integer == NIA, "First address should be 0"

    for iteration in range(100):
        # Icache load the data at NIA (Next Instruction Address)
        await RisingEdge(dut.i_clk)
        if DEBUG:
            print("Fake Cache is loading address 0x{:x}".format(NIA))
        CIA = NIA
        # Give some time to the Icache to return an instruction
        await Timer(200, units="ps")
        assert dut.cia.value.integer == CIA, """Internal signal CIA should take
                                                            the value from NIA"""
        if DEBUG:
            print("JUMP worked")
        assert dut.o_link_register.value.integer == LR, """Link Register (LK=0) is wrong,
                                                            See ISA section 2.4"""
        assert dut.o_count_register.value.integer == CTR

        # Parameters for the current iteration
        # Conditional Register, see Section 2.3.1 -> CR[32:63]
        CR = utils.random_32b()
        A = utils.random_bit()
        T = utils.random_bit()
        LK = utils.random_bit()
        BI = random.randint(0, 2**5-1)
        # BH: Target address prediction, See Power ISA Section 2.4 Figure 42
        BH = random.randint(0, 3)
        tBO = random.randint(0, 7)  # Type for BO
        BO = generate_BO(tBO=tBO, A=A, T=T)
        old_LR = LR
        LR = expected_LR(LR=LR, CIA=CIA, LK=LK)
        CTR = expected_CTR(CTR=CTR, tBO=tBO)
        # Warning: Always run expected_CTR first
        going_to_branch = False
        if should_branch(tBO=tBO, CR=CR, BI=BI, CTR=CTR):
            going_to_branch = True
            NIA = expected_branch_target_address(old_LR)
        else:
            NIA = CIA + 4

        # Print information about the current iteration for debugging purpose
        if DEBUG == True:
            print("Sending XL-form Conditional Branch to Link Register:")
            print(f"\tLR = 0x{old_LR:>x} = 0b{old_LR:>064b}")
            print(f"\tCIA = 0x{CIA:>x} = 0b{CIA:>064b}")
            print(f"\tCR = 0x{CR:>x} = 0b{CR:>032b}")
            print("\tOP = 19 = 0b010011 (Branch conditional to Link Register XL-form)")
            print(
                f"\tBO = 0x{BO:>x} = 0b{BO:>05b} (type: {tBO} - {str_tBO(tBO)})")
            print(f"\tBI = {BI} = 0x{BI:>x} = 0b{BI:>05b}")
            print(f"\tBD = 0x{BH:>x} = 0b{BH:>014b} "
                  f"({str_BH(BH,'bclr')})")
            print(f"\tLK = {LK}")
            print(f"Expected to branch: {going_to_branch}")
            print(f"Expected NIA: 0x{NIA:>x} = 0b{NIA:>064b}")
            print(f"Expected LR: 0x{LR:>x} = 0b{LR:>064b}")
            print(f"Expected CTR: 0x{CTR:>x} = 0b{CTR:>064b}")

        dut.i_instr.value = int(utils.branch_xl_form_to_string(
            PO=19, BO=BO, BI=BI, BH=BH, XO=16, LK=LK)[:32], 2)
        dut.i_stall.value = 0b0  # No stall
        dut.i_en.value = 0b1  # This is a branch
        dut.i_i_form.value = 0b0
        dut.i_b_form.value = 0b0
        # Branch conditional to Link Register XL-form like described in Section 2.4
        dut.i_cond_LR.value = 0b1
        dut.i_cond_CTR.value = 0b0
        dut.i_cond_TAR.value = 0b0
        dut.i_condition_register.value = CR
        dut.i_target_address_register.value = utils.random_64b()
        await Timer(100, units="ps")  # Give time for the combinatinal logic
        assert dut.o_next_instr_addr.value.integer == NIA, f"NIA should be {NIA:>x} not {dut.o_next_instr_addr.value.integer:>x}"


def str_BH(BH: int, t: str) -> str:
    """
    t can be "bclr" "bcctr" "bctar"
    """
    if BH == 0b00 and t == "bclr":
        return "The instruction is a subroutine return"
    elif BH == 0b00 and (t == "bcctr" or t == "bctar"):
        return "Target address is likely to be the same as the last time the branch was taken"
    elif BH == 0b01 and t == "bclr":
        return "Target address is likely to be the same as the last time the branch was taken"
    elif BH == 0b01 and (t == "bcctr" or t == "bctar"):
        return "Reserved"
    elif BH == 0b11:
        return "Target address is not predictable"
    else:
        return "Error"


def str_tBO(tBO: int) -> str:
    if tBO == 0:
        return "Decrement CTR; Branch if CTR!=0 and CR[BI]=0"
    elif tBO == 1:
        return "Decrement CTR; Branch if CTR=0 and CR[BI]=0"
    elif tBO == 2:
        return "Branch if CR[BI]=0"
    elif tBO == 3:
        return "Decrement CTR; Branch if CTR!=0 and CR[BI]=1"
    elif tBO == 4:
        return "Decrement CTR; Branch if CTR=0 and CR[BI]=1"
    elif tBO == 5:
        return "Branch if CR[BI]!=0"
    elif tBO == 6:
        return "Decrement CTR; Branch if CTR!=0"
    elif tBO == 7:
        return "Decrement CTR; Branch if CTR=0"
    else:
        return "Always Branch"


def expected_branch_target_address(LR) -> int:
    LR_0_61 = f"{LR:>064b}"[:62]
    branch_target_address = int(LR_0_61 + "00", 2)
    # Safety check
    if branch_target_address != (LR & 0xfffffffffffffffc):
        print(f"Error: LR=0x{LR:>x}")
        print(f"One says: {branch_target_address}")
        print(f"The other: {LR & 0xfffffffffffffffc}")
    assert branch_target_address == (LR & 0xfffffffffffffffc)
    return branch_target_address


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


def expected_LR(LR, CIA, LK):
    if LK == 1:
        return CIA+4  # Effective address of the instruction following the Branch Instruction
    return LR


def should_branch(tBO, CR, BI, CTR) -> bool:
    if tBO == 0:
        return utils.select_bit(
            reg=CR, size=32, bit=BI) == 0 and CTR != 0  # CTR[0:63]
    elif tBO == 1:
        return utils.select_bit(
            reg=CR, size=32, bit=BI) == 0 and CTR == 0
    elif tBO == 2:
        return utils.select_bit(reg=CR, size=32, bit=BI) == 0
    elif tBO == 3:
        return utils.select_bit(
            reg=CR, size=32, bit=BI) == 1 and CTR != 0
    elif tBO == 4:
        return utils.select_bit(
            reg=CR, size=32, bit=BI) == 1 and CTR == 0
    elif tBO == 5:
        return utils.select_bit(reg=CR, size=32, bit=BI) == 1
    elif tBO == 6:
        return CTR != 0
    elif tBO == 7:
        return CTR == 0
    else:
        return True


def generate_BO(tBO, A, T) -> int:
    if tBO == 0:
        # Decrement CTR then branch if CTR[M:63] != 0 and CR[BI] == 0
        return utils.random_bin("0000?")
    elif tBO == 1:
        # Decrement the CTR then branch if CTR[M:63] == 0 and CR[BI] == 0
        return utils.random_bin("0001?")
    elif tBO == 2:
        return 0b00100 | A << 1 | T  # Branch if CR[BI] == 0
    elif tBO == 3:
        # Decrement the CTR, then branch if CTR[M:63] != 0 and CR[BI] == 1
        return utils.random_bin("0100?")
    elif tBO == 4:
        # Decrement the CTR, then branch if CTR[M:63] == 0 and CR[BI] == 1
        return utils.random_bin("0101?")
    elif tBO == 5:
        return 0b01100 | A << 1 | T  # Branch if CR[BI] == 1
    elif tBO == 6:
        # Decrement the CTR, then branch if CTR[M:63] != 0
        return 0b10000 | A << 3 | T
    elif tBO == 7:
        # Decrement the CTR, then branch if CTR[M:63] == 0
        return 0b10010 | A << 3 | T
    else:
        return utils.random_bin("1?1??")  # Branch always

# TODO Improve coverage of CTR==0
