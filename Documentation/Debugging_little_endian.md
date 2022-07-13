# Debugging little endian

Because we support both little endian and big endian you may get confused.
Here are some examples which may help you debug in both modes.

## Hello world
Start with a simple C program.
```C
// Call this file main.c
#include <stdio.h>
void test(void) {
    printf("Example\n");
}
int main(int argc, char **argv) {
    test();
    return 0;
}
```

## Big Endian
You can compile you program with:
```bash
powerpc64-linux-gnu-gcc-10 main.c -o test
```
You can now disassemble the binary (`test`) with:
```bash
powerpc64-linux-gnu-objdump -D test
```
You can see the code for the `main` function:
```
 aac:	7c 08 02 a6 	mflr    r0
 ab0:	f8 01 00 10 	std     r0,16(r1)
 ab4:	fb e1 ff f8 	std     r31,-8(r1)
 ab8:	f8 21 ff 81 	stdu    r1,-128(r1)
 abc:	7c 3f 0b 78 	mr      r31,r1
 ac0:	7c 69 1b 78 	mr      r9,r3
 ac4:	f8 9f 00 b8 	std     r4,184(r31)
 ac8:	91 3f 00 b0 	stw     r9,176(r31)
 acc:	4b ff ff 99 	bl      a64 <.test>
 ad0:	39 20 00 00 	li      r9,0
 ad4:	7d 23 4b 78 	mr      r3,r9
 ad8:	38 3f 00 80 	addi    r1,r31,128
 adc:	e8 01 00 10 	ld      r0,16(r1)
 ae0:	7c 08 03 a6 	mtlr    r0
 ae4:	eb e1 ff f8 	ld      r31,-8(r1)
 ae8:	4e 80 00 20 	blr
```
You can compare this with the OpenPower ISA v3.1.
If you look at the `blr` instruction (address `0xae8`).
The first 8 bits are `0x4e` or `0b01001110`.
According to the ISA the bits 0 to 5 contains the opcode.
Here it is `0b010011` or `19` in decimal (Just discard the bits on the right).
In the ISA, Figure 91 "Power ISA AS Instruction Set Sorted by Opcode" you can
see that it matches a Branch to Link Register.

## Little Endian
You can compile using the little endian version of the compiler:
```bash
powerpc64le-linux-gnu-gcc-10 main.c -o test_le
```
You can disassemble it with:
```
powerpc64le-linux-gnu-objdump -D test_le
```
You get the following code:
```
 8cc:	02 00 4c 3c 	addis   r2,r12,2
 8d0:	34 76 42 38 	addi    r2,r2,30260
 8d4:	a6 02 08 7c 	mflr    r0
 8d8:	10 00 01 f8 	std     r0,16(r1)
 8dc:	f8 ff e1 fb 	std     r31,-8(r1)
 8e0:	c1 ff 21 f8 	stdu    r1,-64(r1)
 8e4:	78 0b 3f 7c 	mr      r31,r1
 8e8:	78 1b 69 7c 	mr      r9,r3
 8ec:	28 00 9f f8 	std     r4,40(r31)
 8f0:	e6 01 09 7c 	mtfprwz f0,r9
 8f4:	20 00 3f 39 	addi    r9,r31,32
 8f8:	ae 4f 00 7c 	stfiwx  f0,0,r9
 8fc:	89 ff ff 4b 	bl      884 <test+0x8>
 900:	00 00 20 39 	li      r9,0
 904:	78 4b 23 7d 	mr      r3,r9
 908:	40 00 3f 38 	addi    r1,r31,64
 90c:	10 00 01 e8 	ld      r0,16(r1)
 910:	a6 03 08 7c 	mtlr    r0
 914:	f8 ff e1 eb 	ld      r31,-8(r1)
 918:	20 00 80 4e 	blr
```
You need to read the hexadecimal representation from right to left.
`20 00 80 4e` becomes `4e 80 00 20` and you end up with the Big Endian
representation.
