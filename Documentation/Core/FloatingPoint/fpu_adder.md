# Module: Floating Point Unit (FPU) - Adder

## Vanilla version
Source file is [Logic/Core/FloatingPoint/fpu_adder_vanilla.sv](Logic/Core/FloatingPoint/fpu_adder_vanilla.sv)

## See also

## Website simulation
Here is a website with an IEEE-754 Floating Point Converter: https://www.h-schmidt.net/FloatConverter/IEEE754.html

## Python example
```python
import numpy
import struct
def binary_32b(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))
def binary_64b(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!d', num))

binary_64b(numpy.float64(1+2**-52))
# 0_01111111111_0000000000000000000000000000000000000000000000000001
# Sign=0 (+)
# Exponent = 0b01111111111 - 1023 = 0
# Significant= 1 + 0*2**-1 + 0*2**-2 + ... + 12*2**-52
```
### Research papers
#### Delay-optimized implementation of IEEE floating-point addition
The work of P.M.Seidel and G.Even give a good overview of the 2004 FPU adder designs.
DOI: 10.1109/TC.2004.1261822

In an earlier paper only XOR delay was used, the authors are now also using FO4 delays to estimate
how fast the design is.
With a 15.3 FO4 delay per stage between latches.
Be aware that delay estimation using the logical effort model is just a nice approximation and real
performance can only be measured when taped-out. (Especially with today's techonology node)

See: `Logical Effort: Designing Fast CMOS Circuits by David L.Harris`

TODO implement and benchmark against other implementation

#### An IEEE Compliant Floating-Point Adder that conforms with the pipelined packet-forwarding paradigm
By Asger Munk Nielsen, David W. Matula
DOI: 10.1109/12.822562

Notes:
- Good introduction to the basic algorithm (vanilla). 
- Good introduction to the near/far path optimisation
- Talks about combining rounding with the addiction of the significants using a compound adder
- Modern CPU require 2-4 Clock Cycle for FP addition
- 15 Logic Levels per pipeline stage, 2 stages
- Good for successive dependent FP operations.

TODO implement and benchmark against other implementation

### Berkeley hardfloat
Link to their project: https://github.com/ucb-bar/berkeley-hardfloat

### Simple FPU by Danshanley
https://github.com/danshanley/FPU/blob/master/fpu.v

Notes:
- simple Behavioral modelisation in Verilog
- Takes 2 single precision (32-bit) inputs `a` and `b`
- Returns a single precision `out`
- No rounding mode (How is it IEEE 754 compliant?)
- Do not follow industry pratice: "Use non-blocking assignments for all sequential logic"
- Do not follow our coding style: Tend to put everything in big `always @*` blocks
- Do not follow our coding style: Reassign signal (see [o_mantissa](https://github.com/danshanley/FPU/blob/aff7125b605ad4c7d933af983c105fc6a9c4f5b9/fpu.v#L250))
- Provide a `show_rtl.ys` to run yosys on the design
- No pipelining

#### Data path (for the adder only) is as follow:
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

#### About the verification:
- a `testgen.py` python script is provided
- It uses numpy `np.float32` as a reference
- It generates a very simple `fpu_tb.v` verilog testbench
- Checks if the difference between the decimal representation of the output and the expected output
is bigger than 2.
- Do not close the file at the end of the script

### CVFPU
FMA: https://github.com/openhwgroup/cvfpu/blob/develop/src/fpnew_fma.sv

See ["Fpnew: An open-source multiformat floating-point unit architecture for energy-proportional
transprecision computing"](https://arxiv.org/abs/2007.01530) by Mach, Stefan and Schuiki, Fabian and Zaruba, Florian and Benini, Luca.


Notes:
- Written in Verilog
- Lots of parameters
- Code is clean and readable
- Readme says it is compliant with IEEE 754-2008, support for halft/single/double/quad-precision
- Division has some compliancy issue with IEEE 754-2008
- Good interface specification and architecture overview: https://github.com/openhwgroup/cvfpu/blob/develop/docs/README.md
- Packed arrays only (for EDA compatibility)
- valid/ready handshake interface
- [Have a config to enable/disable more/less pipeline stages](https://github.com/openhwgroup/cvfpu/blob/0fc3620978a500303ce94811eec7839e427dc995/src/fpnew_fma.sv#L72-L86)
- Using valid/ready handshake between the hierarchy levels to allow clock-gating and increase energy efficiency.
- Require synthesis tool to do pipeline "retiming"
- Round-robin output arbiter

Remarks:
- How much overhead is it to use a Multiply-Add module just to Add (or Multiply)?
- How good it the design (without retiming) balenced? The first stage contains an exponent
  difference, significant shift and the sum of the operands.
- If a special result (inf, nan...) is detected stage 0, it stays in the pipeline. Can it 'retire'
  stage 0 and therefore save resources/improve latency? (It would require an extra "early result"
  output to the module to be able to return special results at the same time as normal results)

#### Data path (64b adder part only):
- [Start with operands](https://github.com/openhwgroup/cvfpu/blob/0fc3620978a500303ce94811eec7839e427dc995/src/fpnew_fma.sv#L30) `operands_i`
Input stage:
- Store `operands_i` in the first pipeline stage `inp_pipe_operands_q[0]`

Classify input:
- Module `fpnew_classifier` identifies if the operand is zero, inf, nan...
- Invert sign of `operand_a` if we are to perform a substraction

Input classification:
- Check for infinity, nan
- Is it an effective subtraction?

Special case handling
- Bypass FMA and return invalid operation is divide by 0
- Bypass FMA if nan
- Bypass FMA if inf

Initial exponent data path:
- Zero-extend exponents into signed container
- Compute the `exponent_difference` (the operation is expected to be `a*b+c` so they are first
  computing `c`'s exponent (as `exponent_addend`) and `a*b`'s exponent as `exponent_product`)
- Compute `addend_shamt`

Addend data path:
- `mantissa_c` is shifted by `addend_shamt` (resulting in `addend_after_shift`)
- in case of a substraction `addend_after_shift` is inverted

Adder:
- Add `product_shifted` to `addend_shifted`
- Complement negative result (only for effective substractions)
- the significants' `sum` is latched

Normalization:
- `sum_q[108:0]` are passed to `lzc` module to count the number of leading zeros
- Compute `norm_shamt`
- Shift the result (`sum_q`) by `norm_shamt`
- `final_mantissa`: Shift `sum_shifted` again if an overflow occured of if the normalized sum is still denormal

Classification after rounding:
- Module `fpnew_rounding` is in charge of the rounding and output it in `regular_result`
- Select `regular_result` or `special_result_q` (line 624)


#### Verification:
I cannot find anything about their verification methodology.

#### Testing:
TODO test and compare

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
