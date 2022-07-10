# Module: Identify

This module identifies an intruction coming from the instruction fetch (IF).
And sends it to the appropriate decoding unit.

Inputs:
- a 64 bits instruction (only bits 0:31 are used if this is a word instruction.

Outputs:
- 1 bit: Is the instruction a branch
... (TODO)
