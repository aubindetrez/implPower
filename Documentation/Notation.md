# Acronyms / Abbreviation and Vocabulary
- General Purpose Register (GPR)
- Extending (EXT)
- Memory (MEM)
- Special Purpose Register (SPR)
- Current Instruction Address (CIA)
- Next Instruction Address (NIA)
- VSR load and store
- Floating-Point (FP)
- Scalar Fixed-point Subset (SFS). Basic fixed point and load/store instructions. 
- Scalar Fixed-point + Floating-point Subset (SFFS). Adding floating point operations to the Base Architecture.
- Linux Compliancy Subset (LCS). Intended for server grade Linux, adding features like 64-bit, optional SIMD/VSX, Radix MMU, little endian mode and hypervisor support.
- AIX Compliancy Subset (ACS). Intended to run AIX, adding features like decimal and quad precision floating point, big endian mode and symmetric multiprocessing.
- Copy-Paste Accelerator (CPA)
- Secure Memory Facility (SMF)
- Most Significant Byte (MSB)
- octword: 256 bits
- quadword: 128 bits
- doubleword: 64 bits
- word: 32 bits
- half-word: 16 bits
- byte: 8 bits
- nibble: 4 bits
- Condition Register (CR)
- Link Register (LR)
- Count Register (CTR)
- Fixed-Point Exception Register (XER)
- Vector-Register Save Register (VRSAVE)
- General Purpose Register (GPR)
- Floating-Point Register (FPR)
- Floating-Point Status and Control Register (FPSCR)
- Vector Register (VR)
- Vector Status and Control Register (VSCR)
- Vector-Scalar Register (VSR)
- word instruction = a 32 bits instruction
- prefixed instruction = a 64 bits instruction
- Primary Opcode (PO)
- Extended Opcode (XO)
- Expanded Opcode (EO)
- Branch History Rolling Buffer (BHRB)
- opcode
- Subtype (ST). a bit which specifies the subformat uses by an instruction.
- Load Store (LS)
- Effective Address (EA)
- (RA) is a field in the instruction
- err. Short for "Error", all signals starting with `err_` are in the design to
  help debugging
- dbg. Short for "Debug", all signals starting with `dbg_` are in the design to
  help with debugging
- addr. Short for "Address"

# Notation
I am using the same notation at the PowerISA.
- RT, RA, R1 refer to the General Purpose Registers.
- FRT, FRA, FR1 refer to the Floating-Point Registers.
- FRTp, FRAp, FRBp refer to an even-odd pair of Floating-Point Registers
- VRT, VRA, VR1 refer to Vector Registers
- Byte 0 is the Most Significatn Byte (MSB)
- 8LS refers to 8 bytes Load / Store
