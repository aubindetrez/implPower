# Architecture

This is a work in progress, this document contains notes about the
architecture.

## Graph
TODO High level graph of the entire architecture

## Basic classes of instructions
Instructions are 4 bytes (32 bits = 1 word) or 8 bytes (64 bits = doubleword)
long.
All instructions are word (32 bits) aligned and therefore the address' lower 2
bits are ignored.

### Registers
Condition Register (CR)
Link Register (LR)
Count Register (CTR)
Fixed-Point Exception Register (XER)
Vector-Register Save Register (VRSAVE)
32 General Purpose Registers (GPRs)
32 Floating-Point Registers (FPRs)
Floating-Point Status and Control Register (FPSCR)
32 Vector Registers (VRs)
Vector Status and Control Register (VSCR)
64 Vector-Scalar Registers (VSRs)

### Instructions / Registers
- Scalar fixed-point instruction work on General Purpose Registers (GPRs)

- Vector fixed-point instructions work on Vector Registers (VRs)

- Scalar binary floating-point instructions work on Floating Point Registers
(FPRs) or Vector-Scalar Registers (VSRs).

- Scalar decimal floating-point instructions work on Floating Point Registers
  (FPRs)

- Vector floating-point instructions work on Vector Registers (VRs) or
  Vector-Scalar Registers (VSRs)

### Computation modes
Two computation modes: 32 and 64 bits
It affects:
- how the effective address is interpreted
- how Condition Register (CR) bits are set
- how Fixed-Point Exception Register (XER) bits are set.
- how the Link Register (LR) is set by branch instructions
- how the Count Register (CTR) is tested by Conditional Branches 
Almost all instructions are available in both modes (except some GPR Scalar
fixed point instructions)

In 32 bits mode high-order 3s bits of the computed effective address are
ignored when addressing storage.

The address of a prefixed instructions (64b) is the address of its prefix
(first 32b).

If a prefixed instructions (64b) crosses a 64-bytes boundary the system
alignment error handler is invoked.

### Instruction formatting
Instruction formatting is discussed in the ISA (v3.1) page 12 to 22.

Prefixed instructions' primary opcode (bits 0:5) are `0b00_0001`.
If bit 6 is set then the suffix (lower 32 bits) is a defined word instruction.
Else if bit 6 is not set then the suffix is not a defined word.
