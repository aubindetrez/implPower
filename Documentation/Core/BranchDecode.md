# Module: Branch Decode

See Power ISA section 2.4

This module takes an identified intruction from the Identify unit 
[Documentation/Core/Identify.md](Documentation/Core/Identify.md).
and sends it to the Arbiter with informations the Arbiter needs to avoid hazards (and do register
renaming...).

Interface:
- `i_clk`
- `i_rst`
- `i_en`
- `i_instr_suffix`
- `i_instr_prefix`

TODO Branch History Rolling Buffer (BHRB) Chapter 7 / Book II page 1111

Branch Facility (Power ISA Chapter 2 page 59):
- `b`, `ba`, `bl`, `bla`:
    - Read: CIA
    - Write: LR, NIA
    - Exception: TODO
- `bc`, `bca`, `bcl`, `bcla`:
    - Read: CTR, CIA, CR
    - Write: CTR, LR, NIA
    - Exception: TODO
- `bclr`, `bclrl`:
    - Read: CIA, CTR, CR
    - Write: NIA, CTR, LR
    - Exception: TODO
- `bcctr`, `bcctrl`:
    - Read: CR, CTR, CIA
    - Write: NIA, LR
    - Exception: TODO
- `bctar`, `bctarl`:
    - Read: CTR, CR, CIA
    - Write: NIA, CTR, LR
    - Exception: TODO

TODO Event-Based Branch Facility (Power ISA Chapter 6 page 1133):

TODO Power ISA Book 3 Chapter 4 page 1153

TODO Book 2 Chapter 6 Section 6.3.1 Implicit Branch page 1189

TODO Event-Based Branch Exception Ordering page 1306

TODO Performance Monitor Facility / Branch History Rolling Buffer page 1343




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
