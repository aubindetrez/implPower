# Module: Arbiter

The Arbiter takes a decoded instruction as input and:
- Stores the instruction in a queue (aka reservation station RS)
- If a queue is full then `o_full_mask` will be set so instruction fetch (IF) will be paused if
an instruction belonging to the queue (the full one) is identified.
- Checks for Data hazards, RAW, WAR and WAW
- If it's operands are available it fetches them from the register file. If not then it stores
  which previous instruction will produce the operand (thus providing register renaming).
- Checks for structural hazards (is a matching functional unit available?)
- If an all dependencies are met + an execution unit is free then it sends the instruction and its
operands for execution. This part is **out of order**
- When instructions finish executing (aka retire) the Arbiter reads their results on the Common
  Data Bus (CDB) and write the Register File (RF), handles execeptions and write memory (Stores)
  **in order**

Interface:
- `o_full_mask` A mask to tell the Identify Unit to stall Fetching as soon as a certain type of
instruction is idenfied.
- `i_identify_unknown_instr` Raised by the Identify module because an instruction cannot be
  identified. According to section 1.9 of the ISA a System Illegal Instruction error handler must
  be called. Stop fetching (stall) and wait for all instructions to retire before calling the
  handler. If one of the in-flight instruction (yet to be retire) raises an exception then it has a
  higher priority, once all the other exceptions are handled the System Illegal Instruction error
  handler can be called. (Unless one of the prior exception handler changed the CIA).

TODO continue description of the arbiter as work on functional units continues

## Idea for later
- Implement Store forwarding: If a load follows a store with the same effective address (EA) then
just forward the result.

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

## Learn more about it
See
[https://en.wikipedia.org/wiki/Tomasulo%27s_algorithm](https://en.wikipedia.org/wiki/Tomasulo%27s_algorithm)
to learn about Tomasulo's algorithm.
[Conversion from Tomasulo to Scoreboards on LibreSOC](https://libre-soc.org/3d_gpu/architecture/tomasulo_transformation/)
[6600 Scoreboad discussion](https://libre-soc.org/3d_gpu/architecture/6600scoreboard/)
[Wikipedia's article about RISC-V Pipeline](https://en.wikipedia.org/wiki/Classic_RISC_pipeline#Hazards)
[Difference between Intel Micro-Architecture and Tomasulo's algorithm](http://adusan.blogspot.com/2010/11/differences-between-tomasulos-algorithm.html)
