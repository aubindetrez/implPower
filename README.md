# implPower
I small open implementation of the Power ISA v.3.1

## Status
This is a work in progress, no working prototype yet but let me know if you are
interrested (just open a friendly issue ;) ).

## The Power ISA
For more information about the Power ISA see the Wikipedia page: https://en.wikipedia.org/wiki/Power_ISA

## Common questions
- What is GPR, CTR... ?
[Documentation/Notation.md](Documentation/Notation.md) contains all the
acronyms and abbreviations used in this project.

- I want to learn about this project, where to get started?
This project is in a very early stage of development there isn't much to be
seen yet. (TODO: Update with a Getting Started Guide and a presentation)
You can start with the presentation of the Architecture [Documentation/Architecture.md](Documentation/Architecture.md)

## How to simulate
TODO

## Code for Power ISA
### Compile with gcc
To install a cross compiler for OpenPower, on Debian/Ubuntu you can:
```bash
sudo apt install gcc-10-powerpc64-linux-gnu gcc-10-powerpc64le-linux-gnu
```
You can then compile with `powerpc64le-linux-gnu-gcc-10` (for Little Endian) and for Big Endian: `powerpc64-linux-gnu-gcc-10`.
If you want to read more about little/big endian you can read:
[Documentation/Debugging_little_endian.md](Documentation/Debugging_little_endian.md)
### Alternative toolchain
You can also get a full toolchain from: https://github.com/advancetoolchain/advance-toolchain

Here is an example for debian
```bash
sudo apt install autoconf-archive debhelper docbook2x dpkg-sig libncurses5-dev libxml2-utils systemtap-sdt-dev texinfo xutils-dev
# Download the latest release Advance Toolchain
wget https://github.com/advancetoolchain/advance-toolchain/archive/refs/tags/at15.0-3.tar.gz
tar xvzf at15.0-3.tar.gz
cd advance-toolchain-at15.0-3/
sudo make all AT_CONFIGSET=15.0
```
## Run a custom program on the simulator
TODO Explain how to run a custom program on the high level model
TODO Explain how to run a custom program on the verilog model

## Build and boot linux
TODO

## How to map on an FPGA
TODO

## How to get GDSII
TODO

## How to contribute
If you are just starting you journey to hardware here are some resources just
for you: (May be outdated, I don't plan to maintaining this list)
- Writing python scripts
- Computer architecture (Computer Architecture: A Quantitative Approach by John L. Hennessy, David A. Patterson, Krste Asanovi)
- Basic SystemVerilog/Verilog RTL design http://www.asic-world.com/verilog/veritut.html
- Logical effort http://bwrcs.eecs.berkeley.edu/Classes/icdesign/ee141_f05/Lectures/Notes/ComputingLogicalEffort.pdf
- General VLSI design (CMOS VLSI Design: A Circuits and Systems Perspective by Neil Weste, David Harris)
- Understand how synthesis works and be aware of it when writing RTL
- Basic understanding of Static Timing Analysis
- Timing closure basics (Efabless' guide: https://docs.google.com/document/d/13J1AY1zhzxur8vaFs3rRW9ZWX113rSDs63LezOOoXZ8/edit#heading=h.9y68197ebff7)
- Read open source code to get familiar with it (example: https://github.com/lowRISC/ibex)
- What subset of SystemVerilog is synthesizable.
- How do we initialize registers and bringup a chip in a known state
- Clock Gating / Data Gating

How to contribute:
- Create a directory and write a testbench in [FuncVerif/](FuncVerif/)
Just create a `test.sh` script which runs your checks and returns `0` on a success.
Also write a `clean.sh` to clean all your products. I recommand to use cocotb,
verilator, iverilog or yosys but it you want to use some other tool you can.
- Write your design in [Logic/](Logic/)
- Optional: You can use formal verification (using yosys)
- Optional: You can also use simple SystemVerilog testbenches (cf [Tools/simu](Tools/simu) )
- Optional: You can synthetize your design in And Inverter Graph to get an idea about the depth and complexity (cf [Tools/synth_aig](Tools/synth_aig) )
- Optional: You can synthetize your design for 130/45/15/7nm and run Static Timing Analysis on it (cf [Tools/synth_sky130](Tools/synth_sky130),  [Tools/synth_ng45](Tools/synth_ng45) )
- Optional: You can synthetize your design for FPGA (cf [Tools/synth_xil](Tools/synth_xil) )
- Optional: You can try your design on an actual FPGA
- Optional: You can use OpenLane to check how it would perform on 130nm https://github.com/The-OpenROAD-Project/OpenLane
- Run all the sanity checks before pushing your changes: [check_before_commit.sh](check_before_commit.sh)

Here are some verilog coding guidelines: [Documentation/Coding_guidelines.md](Documentation/Coding_guidelines.md)
## See also
- A2I POWER: Power ISA v.2.06 compliant core: https://github.com/openpower-cores/a2i
- A2O POWER: Power ISA v.2.07 compliant core: https://github.com/openpower-cores/a2o
- Microwatt: Power ISA v.3.0 compliant core: https://github.com/antonblanchard/microwatt
- Chiselwatt: https://github.com/antonblanchard/chiselwatt
