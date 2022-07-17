# Branch Facility
Branch Facility is described in the Power ISA v3.1, (Chapter 2, page 33).

Section 2.4 and (1.10.3) describes 5 cases of effective address calculation.

- If Branch Instruction -> compute and fetch the branch target address
- If Trap Instruction -> test the trap condition and call a handler
- If System Call -> call a handler
- If System Call Vectored -> call a handler
- If Event-based exception -> call event-based branch handler (Book II Chapter 6)
- If Exception -> call system error handler (Section 1.9 page 25)
- If Returning from System Service program
- If Returning from Trap handler
- If Returning from System Error handler
- Else Sequential execution (auto-increment the Current Instruction Address CIA +4B)

## Design choices
In order to start with a simple first design when a branch is decoded no more
instructions are fetched until the Next Instruction Address is resolved (no
speculative execution). Instructions which are already in the pipeline will
execute and the instruction fetch will resume when the branch is resolved (can
be taken or not).
This implies: The branch facility needs to have dedicated resources (like a 64b
adder) in order to resolve branches quickly and therefore avoid the fetching
stage to stall.

## Effective Address
Effective Address Calculation is discussed in the Power ISA, page 29.

## Example: How to decode I-form Branches
Here is an I-form Branch Instruction (generated using `objdump`, see [Debugging_little_endian.md](Debugging_little_endian.md))
```
0000000000000a24 <.test>
...
a84:	4b ff ff a1 	bl      a24 <.test>
...
```
The binary representation would be `0100 1011 1111 1111 1111 1111 1010 0001`
According to the Power ISA section 2.4 you can decode it:
- OP = 18 (bits 0 to 5) -> This is a I-form branch
- LI = `1111 1111 1111 1111 1110 1000` (bits 6 to 29)
- AA = 0 (Relative jump) (bit 30)
- LK = 1 (bit 31) -> The Link Register will updated (`CIA + 4 = 0xa84 + 4 = 0xa86`)

To calculate the branch target address you can:
Shift LI to the left: `LI || 0b00 == 1111 1111 1111 1111 1110 1000 00`
This is a negative number, egual to `-96` which makes sense since `0xa84`
(address of the `bl` instruction) if `96` bytes away from `.test` at address
`0xa24`.

## Example: How to decode B-form Branches
TODO disassemble a problem and decode the instruction like I did for I-form Branches

## Example: How to decode Branch to Link Register

## Other open-source projects

### Microwatt
TODO check Microwatt branch unit
Microwatt can be found on github: https://github.com/antonblanchard/microwatt

### A2I
TODO check A2I branch unit
A2I can be found on github: https://github.com/openpower-cores/a2i

### A2O
TODO check A2O branch unit
A2O can be found on github: https://github.com/openpower-cores/a2o

### Ibex (LowRISC RISC-V)
TODO check Ibex branch unit

### Rocket-Chip (RISC-V)
TODO check Rocket-Chip branch unit
Rocket-Chip code can be found on github: https://github.com/chipsalliance/rocket-chip

### Papers
TODO reference research papers and write an overview

## Performance
TODO add information about design choices regarding performance, power, area (and cost)

## Verification
TODO add verification Status

## Physical Design
### Synthesis
- TODO synthesis for SKY130
    - Number/Type of gates
    - Logical Depth (or FO4?)
- TODO synthesis for FreePDK45...
- TODO synthesis for AIG...
- TODO synthesis for Xilinx7...

### Static analysis
- TODO Timing
- TODO Power

### Post Place and Route (PnR)
- TODO Timing
- TODO Power
- TODO Area
