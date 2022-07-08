# Compliancy to Power Power ISA v.3.1
You can watch "The Open Power ISA: Architecture Compliancy and Future Foundations" on Youtube: https://youtu.be/ZGvEpd4vNK0

Full v3.1 ISA 1419 instructions (including all optional features)

This implementation must:
- Support the Base Architecture
- Support either: SFS, SFFS, LCS or ACS


Always Optional (320 instructions):
- Copy-Paste Accelerator CPA
- Secure Memory Facility SMF
- Data Stream Prefetch STM
- Non-coherent Memory M=0
- Write Through Memory Request W=1
- Power Management
- Matrix math

Other:
- Support custom extensions using the architecture sandbox
- Use firmware to help with compliancy


No partial implementation of an optional feature.

## Terminology
- Scalar Fixed-point Subset - SFS. 129 instructions. Basic fixed point and load/store instructions. 
- Scalar Fixed-point + Floating-point Subset - SFFS. 214 instructions. Adding floating point operations to the Base Architecture.
- Linux Compliancy Subset - LCS. 962 instructions. Intended for server grade Linux, adding features like 64-bit, optional SIMD/VSX, Radix MMU, little endian mode and hypervisor support.
- AIX Compliancy Subset - ACS. 1099 instructions. Intended to run AIX, adding features like decimal and quad precision floating point, big endian mode and symmetric multiprocessing.
