# Module: Floating Point Unit (FPU) - Adder

## Vanilla version
Source file is [Logic/Core/FloatingPoint/fpu_adder_vanilla.sv](Logic/Core/FloatingPoint/fpu_adder_vanilla.sv)

## See also

### Research papers
#### Delay-optimized implementation of IEEE floating-point addition
The work of P.M.Seidel and G.Even give a good overview of the 2004 FPU adder designs.
DOI: 10.1109/TC.2004.1261822

XOR and FO4 delays are used to measure performance.
With a 15.3 FO4 delay per stage between latches.
Be aware that delay estimation using the logical effort model is just a nice approximation and real
performance can only be measured when taped-out.

See: `Logical Effort: Designing Fast CMOS Circuits by David L.Harris`

TODO

### An IEEE Compliant Floating-Point Adder that conforms with the pipelined packet-forwarding paradigm
By Asger Munk Nielsen, David W. Matula
DOI: 10.1109/12.822562

TODO

### Berkeley hardfloat
Link to their project: https://github.com/ucb-bar/berkeley-hardfloat

### Small FPU by Danshanley
https://github.com/danshanley/FPU/blob/master/fpu.v

Notes:
- Do not follow industry pratice: "Use non-blocking assignments for all sequential logic"

### CVFPU
https://github.com/openhwgroup/cvfpu

### Sparc64-T1's FPU
https://github.com/freecores/sparc64soc/tree/master/T1-FPU

### Rocket-Chip's FPU
https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/tile/FPU.scala

### Riscy-OOO's FPU
https://github.com/csail-csg/riscy-OOO/tree/master/procs/lib/Fpu.bsv

### MicroWatt's FPU
https://github.com/antonblanchard/microwatt/blob/master/fpu.vhdl

### VexRiscV's FPU
https://github.com/SpinalHDL/VexRiscv/tree/master/src/main/scala/vexriscv/ip/fpu

### Neorv32's FPU
https://github.com/stnolting/neorv32/blob/main/rtl/core/neorv32_cpu_cp_fpu.vhd

### A2I's FPU
https://github.com/openpower-cores/a2i/blob/master/rel/src/vhdl/work/fuq_add.vhdl

### A2O's FPU
According to A2O's Readme it is a 27FO4 3+GHz on 45nm design
https://github.com/openpower-cores/a2o/blob/master/rel/src/verilog/work/fu_add.v
- IEEE 754-1985 compliance
- single and double precesion
- superpipelined

### Commercial

According to [chipandcheese.com](chipandcheese.com)
> K8 can handle FP adds and multiplies with 4 cycle latency, while Netburst takes 5 and 7 cycles respectively
