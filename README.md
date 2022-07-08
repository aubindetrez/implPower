# implPower
I small open implementation of the Power ISA v.3.1

## Status
This is a work in progress, no working prototype yet.

## The Power ISA
For more information about the Power ISA see the Wikipedia page: https://en.wikipedia.org/wiki/Power_ISA

## How to simulate
TODO

## Code for Power ISA
TODO explain how to install GCC and compile for the Open Power ISA

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
TODO

## Verilog coding guideline
In order to be compatible with opensource EDA tools (yosys, iverilog, verilator...)
We program using SystemVerilog and convert it to Verilog using `sv2v`.          
```verilog                                                                          
// Only use comments with "//" do not use "/* ... */"                           
    // Only indent with spaces, no tabulation because of some weird             
    // with propriatory tools                                                   
                                                                                
module <MODULE'S NAME> #(                                                       
    parameter integer <PARAMETER'S NAME> = ... // only use [A-Z_0-9] for constant's names
) (                                                                             
    input logic <INPUT'S NAME>,                                                 
    output logic <INPUT'S NAME>                                                 
);                                                                              
                                                                                
logic [<SIZE>-1:0] <WIRE'S NAME>; // use little endian for packed arrays        
logic <WIRE'S NAME> [<SIZE>-1]; // use big endian for unpacked arrays           
                                                                                
// use "assign" statements (with blocking '=') for combinational logic          
assign <SOME WIRE> = <...>;                                                     
                                                                                
// if using assign is unpractical use combinational blocks                      
always_comb                                                                     
begin                                                                           
    // Only use blocking statements                                             
    a = b; // Such a simple assigment should use "assign"                       
end                                                                             
                                                                                
always_ff                                                                       
begin                                                                           
    // do not use casex and prefer case inside over casez                       
    unique case inside (select)                                                 
        2b'00: e = 1'b0;                                                        
        2b'01: e = ...;                                                         
        default: e = ...; // set defaults even if not required                  
    endcase                                                                     
end                                                                             
                                                                                
// always name your "generate" (if / for...) statements                         
                                                                                
assign big_bit_vector[7:0] = {4'b0000, smaller_vector[3:0]}; // be explicit     
                                                                                
assign counter[3:0] = 4'(counter_q + 4'b1); // explicitely discard the carry    
                                                                                
// Write a testcase using cocotb in verification/<MODULE'S NAME> for every module
// At least check you can synthetise using yosys (default "synth" or AIG)       
```

## See also
- A2I POWER: Power ISA v.2.06 compliant core: https://github.com/openpower-cores/a2i
- A2O POWER: Power ISA v.2.07 compliant core: https://github.com/openpower-cores/a2o
- Microwatt: Power ISA v.3.0 compliant core: https://github.com/antonblanchard/microwatt
