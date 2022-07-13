import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
import cocotb.simulator as simulator

DEBUG = True # Main switch to turn on/off debugging prints

def int_to_bin(n, a):
    form = "{0:0"+str(n)+"b}"
    if a >= 2**n:
        raise TypeError("{} do not fit on {} bits".format(a, n))
        return "0"*n
    return form.format(a)

def branch_i_form_to_string(PO, LI, AA, LK):
    """
    Branch I-form: Section 2.4
    I instruction format Section 1.6.1.7
    0 ---- 6 --------- 30 -- 31 --
       PO       LI        AA    LK
    """
    PO_str = int_to_bin(6, PO)
    LI_str = int_to_bin(24, LI)
    AA_str = int_to_bin(1, AA)
    LK_str = int_to_bin(1, LK)
    result = PO_str + LI_str + AA_str + LK_str
    return result[::-1] # LSB -> MSB

def branch_b_form_to_string(PO, BO, BI, BD, AA, LK):
    """
    Branch Conditional B-form: Section 2.4
    B-FORM Section 1.6.1.2
    0 ---- 6 ---- 11 ---- 16 -------- 30 -- 31 --
       PO     BO      BI        BD       AA    LK
    """
    PO_str = int_to_bin(6, PO)
    BO_str = int_to_bin(5, BO)
    BI_str = int_to_bin(5, BI)
    BD_str = int_to_bin(14, BD)
    AA_str = int_to_bin(1, AA)
    LK_str = int_to_bin(1, LK)
    result = PO_str + BO_str + BI_str + BD_str + AA_str + LK_str
    return result[::-1] # LSB -> MSB

def branch_xl_form_to_string(PO, S1, S2, S3, XO, S4):
    """
    Branch Conditional to Link Register XL-form: Section 2.4
    Branch Conditional to Count Register XL-form: Section 2.4
    Branch Conditional to Branch Target Address Register XL-form: Section 2.4
    XL-FORM Section 1.6.1.18
    0 ---- 6 ---- 11 ---- 16 ---- 21 ---- 31 --
       PO     S1      S2      S3      XO     S4
    S stands for Section
    """
    PO_str = int_to_bin(6, PO)
    S1_str = int_to_bin(5, S1)
    S2_str = int_to_bin(5, S2)
    S3_str = int_to_bin(5, S3)
    XO_str = int_to_bin(10, XO)
    S4_str = int_to_bin(1, S4)
    result = PO_str + S1_str + S2_str + S3_str + XO_str + S4_str
    return result[::-1] # LSB -> MSB

@cocotb.test()
async def test_python_env(dut):
    """
    Unit test for the python verif environment itself (no dut testing)
    """
    # Checking branch_i_form_to_string gives the expect result
    assert branch_i_form_to_string(PO=18, LI=0xcafe, AA=1, LK=1) == "11011111110101001100000000010010"
    assert branch_b_form_to_string(PO=16, BO=18, BI=27, BD=0xafe, AA=1, LK=0) == "01011111110101001101101001000010"
    assert branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=0x16, S4=1) == "10110100000010100010011100110010"

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
    assert dut.dbg_is_prefixed.value == 1, "This is a prefixed instruction"

    dut.i_instr = 0x0000000000000000
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_prefixed.value == 0, "This is not a prefixed instruction"

@cocotb.test()
async def test_identify_branch(dut):
    await init_sequence(dut)
    # Power ISA Section 2.4
    dut.i_instr = int(branch_i_form_to_string(PO=18, LI=0xcafe, AA=1, LK=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_branch_i_form.value == 1, "This is an I form branch"
    assert dut.dbg_is_branch_b_form.value == 0, "This isn't a B form branch but an I form branch"
    assert dut.dbp_is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.dbp_is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.dbp_is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(branch_b_form_to_string(PO=16, BO=18, BI=27, BD=0xafe, AA=1, LK=0), 2)
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_branch_i_form.value == 0, "This is not an I form branch but a B form branch"
    assert dut.dbg_is_branch_b_form.value == 1, "This is a B form branch"
    assert dut.dbp_is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.dbp_is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.dbp_is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=16, S4=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_branch_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.dbg_is_branch_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.dbp_is_branch_cond_to_LR.value == 1, "This is a conditional branch to LR"
    assert dut.dbp_is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.dbp_is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=528, S4=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_branch_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.dbg_is_branch_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.dbp_is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.dbp_is_branch_cond_to_CTR.value == 1, "This is a conditional branch to CTR"
    assert dut.dbp_is_branch_cond_to_TAR.value == 0, "This is not a conditional branch to TAR"

    dut.i_instr = int(branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=560, S4=1), 2)
    await RisingEdge(dut.i_clk)
    assert dut.dbg_is_branch_i_form.value == 0, "This is not an I form branch but a XL form branch"
    assert dut.dbg_is_branch_b_form.value == 0, "This isn't a B form branch but a XL form branch"
    assert dut.dbp_is_branch_cond_to_LR.value == 0, "This is not a conditional branch to LR"
    assert dut.dbp_is_branch_cond_to_CTR.value == 0, "This is not a conditional branch to CTR"
    assert dut.dbp_is_branch_cond_to_TAR.value == 1, "This is a conditional branch to TAR"

# TODO Test this: (Section 1.10.2 - Big-Endian example)
# address 00 -> 00 01 02 03 cmplwi r5, 0
# address 04 -> 04 05 06 07 beq done
# address 08 -> 08 09 0A 0B lwzux r4, r5, r6
# address 0C -> 0C 0D 0E 0F add r7, r7, r7
# address 10 -> 10 11 12 13 "some prefix"
# address 14 -> 14 15 16 17 "some suffix"
# address 18 -> 18 19 1A 1B subi r5, r5, 4
