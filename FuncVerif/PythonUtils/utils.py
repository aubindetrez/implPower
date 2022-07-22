import unittest
import random
import numpy  # For uint64
# Non-Unit specific helper functions for OpenPower verification


def select_bit(reg: int, size: int, bit: int) -> int:
    """
    >>> select_bit(0b0100, 4, 1)
    1
    >>> select_bit(0b0100, 4, 0)
    0
    >>> select_bit(0b0100, 4, 2)
    0
    """
    fmt = "{:0"+str(size)+"b}"
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


def random_bin(string: str) -> int:
    """
    Replace all '?' in the input with a random 0 or 1
    """
    out = ""
    for c in string:
        if c == '?':
            out = out + str(random.randint(0, 1))
        elif c == '0' or c == '1':
            out = out+c
        else:
            raise TypeError("{} is not a 0 or 1".format(c))
            return 0
    return int(out, 2)


def random_bit() -> int:
    return random.randint(0, 1)


def random_32b() -> int:
    return random.randint(0, 2**32-1)


def random_64b() -> int:
    return random.randint(0, 2**64-1)


def exts(num: int, length: int, new_length: int) -> int:
    """ sign-extend an integer of size length to new_length"""
    string = int_to_bin(length, num)
    # MSB is at offset 0
    sign = string[0]
    while len(string) < new_length:
        string = sign + string
    return int(string, 2)


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
    return result + 32*"0"  # Big Endian


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
    return result + 32*"0"  # Big Endian


def branch_xl_form_to_string(PO, BO, BI, BH, XO, LK):
    """
    Branch Conditional to Link Register XL-form: Section 2.4
    Branch Conditional to Count Register XL-form: Section 2.4
    Branch Conditional to Branch Target Address Register XL-form: Section 2.4
    XL-FORM Section 1.6.1.18
    0 ---- 6 ---- 11 ---- 16 ---- 19 ---- 21 ---- 31 --
       PO     BO      BI      //      BH      XO     LK
    S stands for Section
    """
    PO_str = int_to_bin(6, PO)
    BO_str = int_to_bin(5, BO)
    BI_str = int_to_bin(5, BI)
    BH_str = int_to_bin(2, BH)
    XO_str = int_to_bin(10, XO)
    LK_str = int_to_bin(1, LK)
    result = PO_str + BO_str + BI_str + '0'*3 + BH_str + XO_str + LK_str
    assert len(result) == 32
    return result + 32*"0"  # Big Endian

def condreg_xl_form_to_string(PO, BT, BA, BB, XO):
    """
   |0 ---|6 ---|11 ---|16 ---|21 --- | 31
   |  PO |  BT |  BA  |  BB  |   XO  | 0
    """
    PO_str = int_to_bin(6, PO) # 6
    BT_str = int_to_bin(5, BT) # 6+5=11
    BA_str = int_to_bin(5, BA) # +5=16
    BB_str = int_to_bin(5, BB) # 5 = 21
    XO_str = int_to_bin(10, XO) # +10 = 31
    result = PO_str + BT_str + BA_str + BB_str + XO_str + "0"
    assert len(result) == 32
    return result + 32*"0"  # Big Endian


def BE(num: int, length: int) -> int:
    """ Little Endian / Big Endian """
    form = "{:0"+str(length)+"b}"
    bin_ = form.format(num)
    return int(bin_[::-1], 2)


class TestPythonUtils(unittest.TestCase):
    """
    Unit test for the python verif environment itself (no dut testing)
    """

    def test_branch_i_form(self):
        # Checking branch_i_form_to_string gives the expect result
        self.assertEqual(branch_i_form_to_string(PO=18, LI=0xcafe, AA=1, LK=1),
                         "01001000000000110010101111111011"+32*"0")

    def test_branch_b_form(self):
        self.assertEqual(branch_b_form_to_string(PO=16, BO=18, BI=27, BD=0xafe, AA=1, LK=0),
                         "01000010010110110010101111111010"+32*"0")

    def test_branch_xl_form(self):
        #   BO     BO    BI   //  BH      XO      LK
        # 010011 00111 00100 010  10  0000010110  1
        self.assertEqual(branch_xl_form_to_string(PO=19, BO=7, BI=4, BH=0b10, XO=0x16, LK=1),
                         "01001100111001000001000000101101"+32*"0")
    def test_condreg_xl_form(self):
        self.assertEqual(condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6, XO=257),
                "01001100111000110011001000000010"+32*"0")
        self.assertEqual(len(condreg_xl_form_to_string(PO=19, BT=7, BA=3, BB=6, XO=257)), 64)
    def test_exts(self):
        self.assertEqual(exts(0b11, 3, 6), 0b000011)
        self.assertEqual(exts(0b100, 3, 6), 0b111100)

    def test_random(self):
        rd = random_bit()
        self.assertTrue(rd == 0 or rd == 1)
        rd = random_32b()
        self.assertTrue(rd >= 0 and rd <= 2**32-1)
        rd = random_64b()
        self.assertTrue(rd >= 0 and rd <= 2**64-1)

    def test_be(self):
        self.assertEqual(BE(0b10000111, 8), 0b11100001)

    def test_random_bin(self):
        self.assertEqual(random_bin("0110"), 0b110)
        for i in range(5):
            val = random_bin("01?0")
            self.assertTrue(val == 0b110 or val == 0b100)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    unittest.main()
