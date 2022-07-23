import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
import utils
DEBUG = True  # Main switch to turn on/off debugging prints


@cocotb.test()
async def test_condReg(dut):
    """ Test conditional register instructions """
    # Initialization sequence
    clock = Clock(dut.i_clk, 1, units="ns")  # 1ns clock period
    cocotb.fork(clock.start())
    dut.i_rst.value = 0b1
    dut.i_instr.value = 0x0000000000000000
    dut.i_en.value = 0b0
    dut.i_crand.value = 0b0
    dut.i_crnand.value = 0b0
    dut.i_cror.value = 0b0
    dut.i_crxor.value = 0b0
    dut.i_crnor.value = 0b0
    dut.i_creqv.value = 0b0
    dut.i_crandc.value = 0b0
    dut.i_crorc.value = 0b0
    dut.i_mcrf.value = 0b0
    CR = 0b00000000000000000000000000000000

    #output logic [0:31] o_cr // Condition Register (CR)
    #await Timer(200, units="ps")  # reset counters
    for i in range(100):
        await RisingEdge(dut.i_clk)
        await Timer(200, units="ps")
        if DEBUG: print(f"DUT's CR:   0b{dut.o_cr.value.integer:>032b}")
        assert dut.o_cr.value.integer == CR

        dut.i_rst.value = 0b0
        bt = random.randint(0, 2**5-1)
        ba = random.randint(0, 2**5-1)
        bb = random.randint(0, 2**5-1)
        xo = random_xo()
        instr = int(utils.condreg_xl_form_to_string(PO=19, BT=bt, BA=ba, BB=bb, XO=xo)[:32], 2)
        dut.i_instr.value = instr
        dut.i_en.value = 0b1
        dut.i_crand.value = is_crand(xo)
        dut.i_crnand.value = is_crnand(xo)
        dut.i_cror.value = is_cror(xo)
        dut.i_crxor.value = is_crxor(xo)
        dut.i_crnor.value = is_crnor(xo)
        dut.i_creqv.value = is_creqv(xo)
        dut.i_crandc.value = is_crandc(xo)
        dut.i_crorc.value = is_crorc(xo)
        dut.i_mcrf.value = is_mcrf(xo)
        bf = utils.select_bits(reg=instr, size=32, from_=6, to=8)
        bfa = utils.select_bits(reg=instr, size=32, from_=11, to=13)
        if DEBUG: print(f"CR is       0b{CR:>032b}")
        CR = expected_CR(oldcr=CR, xo=xo, bt=bt, ba=ba, bb=bb, bf=bf, bfa=bfa)
        if DEBUG: print(f"expected CR 0b{CR:>032b}")

def replace_bit(size: int, ref:int, offset:int, value: int) -> int:
    """
    >>> replace_bit(size=4, ref=0b0010, offset=2, value=0)
    0
    >>> replace_bit(size=4, ref=0, offset=0, value=1)
    8
    """
    fmt = "{:0"+str(size)+"b}"
    s = fmt.format(ref)
    return int(s[:offset] + str(int(value)) + s[offset+1:], 2)

def get_bit(size: int, var: int, offset: int) -> int:
    """
    >>> get_bit(4, 0b0001, 3)
    1
    >>> get_bit(4, 0b111, 0)
    0
    >>> get_bit(4, 0b1000, 0)
    1
    """
    fmt = "{:0"+str(size)+"b}"
    s = fmt.format(var)
    return int(s[offset])

def expected_CR(oldcr: int, xo: int, bt: int, ba: int, bb: int, bf: int, bfa: int) -> int:
    if xo == 257: # crand
        if DEBUG: print(f"CRAND: CR[{bt}] <- CR[{ba}] & CR[{bb}]")
        val = get_bit(32, oldcr, ba) & get_bit(32, oldcr, bb)
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 225: # crnand
        if DEBUG: print(f"CRNAND: CR[{bt}] <- ~( CR[{ba}] & CR[{bb}] )")
        val = get_bit(32, oldcr, ba) & get_bit(32, oldcr, bb)
        val = not val
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 449: # cror
        if DEBUG: print(f"CROR: CR[{bt}] <- CR[{ba}] | CR[{bb}]")
        val = get_bit(32, oldcr, ba) | get_bit(32, oldcr, bb)
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 193: # crxor
        if DEBUG: print(f"CRXOR: CR[{bt}] <- CR[{ba}] ^ CR[{bb}]")
        val = get_bit(32, oldcr, ba) ^ get_bit(32, oldcr, bb)
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 33: # crnor
        if DEBUG: print(f"CRNOR: CR[{bt}] <- ~( CR[{ba}] | CR[{bb}] )")
        val = get_bit(32, oldcr, ba) | get_bit(32, oldcr, bb)
        val = not val
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 289: # creqv
        if DEBUG: print(f"CREQV: CR[{bt}] <- ~( CR[{ba}] ^ CR[{bb}] )")
        val = get_bit(32, oldcr, ba) ^ get_bit(32, oldcr, bb)
        val = not val
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 129: # crandc
        if DEBUG: print(f"CRANDC: CR[{bt}] <- CR[{ba}] & ~CR[{bb}]")
        val = get_bit(32, oldcr, ba) & (not get_bit(32, oldcr, bb))
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 417: # crorc
        if DEBUG: print(f"CRORC: CR[{bt}] <- CR[{ba}] | ~CR[{bb}]")
        val = get_bit(32, oldcr, ba) | (not get_bit(32, oldcr, bb))
        return replace_bit(size=32, ref=oldcr, offset=bt, value=val)
    elif xo == 0: # mcrf
        if DEBUG: print(f"MCRF: CR[{4*bf} to {4*bf+3}] <- CR[{4*bfa} to {4*bfa+3}]")
        val = get_bit(32, oldcr, 4*bfa)
        oldcr = replace_bit(size=32, ref=oldcr, offset=4*bf, value=val)
        val = get_bit(32, oldcr, 4*bfa+1)
        oldcr = replace_bit(size=32, ref=oldcr, offset=4*bf+1, value=val)
        val = get_bit(32, oldcr, 4*bfa+2)
        oldcr = replace_bit(size=32, ref=oldcr, offset=4*bf+2, value=val)
        val = get_bit(32, oldcr, 4*bfa+3)
        oldcr = replace_bit(size=32, ref=oldcr, offset=4*bf+3, value=val)
        return oldcr
    else: assert false, "xo is wrong"

def random_xo() -> int:
    valid_ops = [33, 289, 129, 417, 257, 225, 449, 193, 0]
    r = random.randint(0, len(valid_ops)-1)
    return valid_ops[r]

def is_crand(xo: int) -> bool:
    return xo == 257
def is_crnand(xo: int) -> bool:
    return xo == 225
def is_cror(xo: int) -> bool:
    return xo == 449
def is_crxor(xo: int) -> bool:
    return xo == 193
def is_crnor(xo: int) -> bool:
    return xo == 33
def is_creqv(xo: int) -> bool:
    return xo == 289
def is_crandc(xo: int) -> bool:
    return xo == 129
def is_crorc(xo: int) -> bool:
    return xo == 417
def is_mcrf(xo: int) -> bool:
    return xo == 0

if __name__ == '__main__':
    import doctest
    doctest.testmod()
