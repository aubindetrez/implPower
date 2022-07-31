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

### Simple FPU by Danshanley
https://github.com/danshanley/FPU/blob/master/fpu.v

Notes:
- Takes 2 single precision (32-bit) inputs `a` and `b`
- Returns a single precision `out`
- simple Behavioral modelisation
- No rounding mode (How is it IEEE 754 compliant?)
- Do not follow industry pratice: "Use non-blocking assignments for all sequential logic"
- Do not follow our coding style: Tend to put everything in big `always @*` blocks
- Do not follow our coding style: Reassign signal (see [o_mantissa](https://github.com/danshanley/FPU/blob/aff7125b605ad4c7d933af983c105fc6a9c4f5b9/fpu.v#L250))
- Provide a `show_rtl.ys` to run yosys on the design

Data path is as follow:
- check if `a` / `b` are normalized and set the mantissa (significant) accordingly
- if `a_exponent = b_exponent`:
    - Compute addition/substraction, results in `o_mantissa` and `o_sign` 
- else:
    - do operand swapping (identify which operand has the biggest exponent)
    - shift the small mantissa by the exponent difference
    - perform addition/subtraction on the mantissa
- Normalize: if mantissa's MSB is `1'b1` (overflow): shift mantissa and increment exponent 
- Normalize: else: use the `addition_normalizer` module (big priority encoder which tests for how many leading
zeros are in the mantissa and shift the mantissa/increment the exponent by the same amount)

Notes about the verification:
- a `testgen.py` python script is provided
- It uses numpy `np.float32` as a reference
- It generates a very simple `fpu_tb.v` verilog testbench
- Checks if the difference between the decimal representation of the output and the expected output
is bigger than 2.
- Do not close the file at the end of the script

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
