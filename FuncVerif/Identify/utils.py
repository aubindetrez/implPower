import unittest
# Non-Unit specific helper functions for OpenPower verification

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

class TestPythonUtils(unittest.TestCase):
    """
    Unit test for the python verif environment itself (no dut testing)
    """
    def test_branch_i_form(self):
        # Checking branch_i_form_to_string gives the expect result
        self.assertEqual(branch_i_form_to_string(PO=18, LI=0xcafe, AA=1, LK=1),
                "11011111110101001100000000010010")

    def test_branch_b_form(self):
        # Checking branch_i_form_to_string gives the expect result
        self.assertEqual(branch_b_form_to_string(PO=16, BO=18, BI=27, BD=0xafe, AA=1, LK=0),
                "01011111110101001101101001000010")

    def test_branch_xl_form(self):
        # Checking branch_i_form_to_string gives the expect result
        self.assertEqual(branch_xl_form_to_string(PO=19, S1=7, S2=4, S3=10, XO=0x16, S4=1),
                "10110100000010100010011100110010")
if __name__ == '__main__':
    unittest.main()
