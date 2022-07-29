# Module: Identify

This module identifies an intruction coming from the instruction fetch (IF).
And sends it to the appropriate decoding unit.

Interface:
- `i_clk` The main core clock
- `i_rst` A reset signal
Active high: When `1'b1` all Latches (Flip-Flops...) resets to their default value.
- `i_en` Enable signal
When low (`1'b0`) inputs are ignored, all internal state stay unchanged.
- `i_instr` a 32 bit instruction

- `o_instr_suffix` a 32-bit instruction, eguals to `i_instr`
- `o_instr_prefix` a 32-bit instruction, contains the prefix if the instruction is prefixed,

- `o_stall_fetch_arb`, active high, stalls the instruction fetch.
  `32'b0` otherwise.
- `i_arb_full_mask`, N-bit (TODO determine the size), coming from the Arbiter, if the in-comming
  instruction matches then `o_stall_fetch_arb` is set to high.  

- `o_branch_identified`, active high, report to the Instruction Fetch (IF) and to the Arbiter
that `i_instr` is a branch.
- `o_condreg_identified`, active high, report to the Arbiter that `i_instr` is a
  conditional register instruction.
- `o_unknown_instr`, active high, report to the Arbiter that the instruction couldn't be identified

Additional information about branch instructions:
- `o_branch_i_form`, Complementary information to decode the branch
- `o_branch_b_form`, Complementary information to decode the branch
- `o_branch_cond_lr`, Complementary information to decode the branch
- `o_branch_cond_ctr`, Complementary information to decode the branch
- `o_branch_cond_tar`, Complementary information to decode the branch

Additional information about condreg (Condition Register) instructions:
- `o_condreg_crand`, Complementary information to decode the Conditional register instruction
- `o_condreg_crnand`, Complementary information to decode the Conditional register instruction
- `o_condreg_cror`, Complementary information to decode the Conditional register instruction
- `o_condreg_crxor`, Complementary information to decode the Conditional register instruction
- `o_condreg_crnor`, Complementary information to decode the Conditional register instruction
- `o_condreg_creqv`, Complementary information to decode the Conditional register instruction
- `o_condreg_crandc`, Complementary information to decode the Conditional register instruction
- `o_condreg_crorc`, Complementary information to decode the Conditional register instruction
- `o_condreg_mcrf`, Complementary information to decode the Conditional register instruction

- TODO identification signals for other instructions
- TODO continue description of the Identify unit as work on the functional units continues

## Principle of operation
The module receives a 32-bit instruction from the Instruction fetch.

It must identify whether the instruction is a branch or not.

Note: when `o_branch_identified` is raised, the instruction fetch (IF) stops fetching new
instruction until the branch is resolved (in order to improve power efficiency).
This prevent control hazards (see
[https://en.wikipedia.org/wiki/Hazard_(computer_architecture)](https://en.wikipedia.org/wiki/Hazard_(computer_architecture))).

It must also identify what "kind" of instruction is it (we can also call it pre-decode).

Note: The arbiter will handle the instruction differently depending on their "kind" (instructions
are grouped together based on what hardware resources their are using (to prevent structural hazard)).

If `i_instr` is a prefixed instruction then the module will not raise any "identified" signal and
fetch the second part of the instruction before proceding with with identification. Prefixed
instruction will be forwarded to the decode stage via `o_instr_prefix` and `o_instr_suffix`.

If the identified instruction matches `i_arb_full_mask` (TODO To be determined) then
`o_stall_fetch_arb` is raised until `i_arb_full_mask` changed and the fetching can proceed.

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
