# Branch Facility
Branch Facility is described in the Power ISA v3.1, (Chapter 2, page 33).

Section 2.4 and (1.10.3) describes 5 cases of effective address calculation.

- If Branch Instruction -> execute the branch target address
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

