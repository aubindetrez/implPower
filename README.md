# implPower
A small open implementation of the Power ISA v.3.1.

The OpenPower ISA can be downloaded from: https://openpowerfoundation.org/specifications/isa/
If I get authorization to distribute this document I will upload it to [Documentation/OPF_PowerISA_v3.1B.pdf](Documentation/OPF_PowerISA_v3.1B.pdf).

## License

This project is licensed under the Creative Commons Attribution 4.0 license.

Please read the OpenPower Power ISA End User License Agreement (In the Open Power ISA document) for more information.
> OPF grants to Recipient the right to license Recipiant Power ISA Cores under the Creative Commons
> Attribution 4.0 license.

## Status
This is a work in progress, no working prototype yet but let me know if you are
interrested (just open a friendly github issue ;) ).

Here are the phases of the project.
- [ ] Vanilla Design/Initial ISA reading: Go through the ISA, make an initial draft. Functinal verification (and formal if needed) is mandatory - instrumentation is optional. (1) [Start: 07/2022]
- [ ] Define some specifications/objectives
- [ ] **Concept**: Document a new micro architecture concept (define units and interfaces) (1)
- [ ] Unit-concept: Document unit micro architectures (1)
- [ ] Optional: write performance model using SystemC like technology
- [ ] **Verification**: Write functional and formal verification with coverage collection for each unit.
- [ ] **Design**: Use the draft's verification code to provide an initial functional coverage and use. (1)
- [ ] Integration: Instrument the design and plug everything together. (1)
- [ ] System verification: Write verification code to drive the entire system and perform sanity checks (1)
- [ ] FPGA testing
- [ ] Final Timing, performance and power analysis. (SKY130 technology?)

1: Static Timing analysis and physical design involved (OpenLane)

We will document each phase/step (especially how good we verified the design).
## The Power ISA
For more information about the Power ISA see the Wikipedia page: https://en.wikipedia.org/wiki/Power_ISA

## Common questions
- What is GPR, CTR... ?
[Documentation/Terminology.md](Documentation/Terminology.md) contains all the
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
- How to read/write timing diagrams
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
- What is equivalence checking (yosys).
- Outdated but a nice read: [Design of a computer: The control data 6600 by J.E. Thornton](https://archive.computerhistory.org/resources/text/CDC/cdc.6600.thornton.design_of_a_computer_the_control_data_6600.1970.102630394.pdf).


How to contribute:
- Create a directory and write a testbench in [FuncVerif/](FuncVerif/)
Just create a `test.sh` script which runs your checks and returns `0` on a success.
Also write a `clean.sh` to clean all your products. I recommand to use cocotb,
verilator, iverilog or yosys but it you want to use some other tool you can.
- Write your design in [Logic/](Logic/)
- Keep it simple: Do not abstact your design more than necessary (Especially if you use Chisel)
- Keep it simple: If you manage to write a very space/time/energy consuming block in just a few
  lines add a comment to make sure any reader know how bad it is.
- Keep it simple: Add comments when things are not obvious
- If you use a special term add it in [Documentation/Terminology.md](Documentation/Terminology.md)
- If you say "Ho, better be carefull about that" or "That is annoying" write it in [Documentation/CommonProblems.md](Documentation/CommonProblems.md)
- Optional: You can use formal verification (using yosys)
- Optional: You can also use simple SystemVerilog testbenches (cf [Tools/simu](Tools/simu) )
- Optional: You can synthetize your design in And Inverter Graph to get an idea about the depth and complexity (cf [Tools/synth_aig](Tools/synth_aig) )
- Optional: You can synthetize your design for 130/45/15/7nm and run Static Timing Analysis on it (cf [Tools/synth_sky130](Tools/synth_sky130),  [Tools/synth_ng45](Tools/synth_ng45) )
- Optional: You can synthetize your design for FPGA (cf [Tools/synth_xil](Tools/synth_xil) )
- Optional: You can try your design on an actual FPGA
- Optional: You can use OpenLane to check how it would perform on 130nm https://github.com/The-OpenROAD-Project/OpenLane
- Run all the sanity checks before pushing your changes: [check_before_commit.sh](check_before_commit.sh) (Tip: You can also configure is as a local git hook)

Here are some verilog coding guidelines: [Documentation/Coding_guidelines.md](Documentation/Coding_guidelines.md)
## See also
- A2I POWER: Power ISA v.2.06 compliant core: https://github.com/openpower-cores/a2i
- A2O POWER: Power ISA v.2.07 compliant core: https://github.com/openpower-cores/a2o
- Microwatt: Power ISA v.3.0 compliant core: https://github.com/antonblanchard/microwatt
- Chiselwatt: https://github.com/antonblanchard/chiselwatt
