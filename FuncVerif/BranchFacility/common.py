import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
import utils


async def init_sequence(dut, mode):
    clock = Clock(dut.i_clk, 1, units="ns")  # 1ns clock period
    cocotb.fork(clock.start())
    dut.i_rst.value = 0b1
    if mode == 32:
        dut.i_32b_mode.value = 0b1  # 32b mode
    elif mode == 64:
        dut.i_32b_mode.value = 0b0  # 64b mode
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

    await Timer(200, units="ps")  # reset counters
    dut.i_rst.value = 0b0
    await Timer(200, units="ps")  # reset counters
    await Timer(200, units="ps")  # reset counters


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
