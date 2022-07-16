import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer


async def init_sequence(dut, mode):
    clock = Clock(dut.i_clk, 1, units="ns")  # 1ns clock period
    cocotb.fork(clock.start())
    dut.i_rst.value = 0b1
    if mode == 32:
        dut.i_32b_mode.value = 0b1  # 32b mode
    elif mode == 64:
        dut.i_32b_mode.value = 0b0  # 64b mode
    else:
        print("Error: init_sequence, {} mode does not exist".format(mode))
        exit(1)
    dut.i_stall.value = 0b0

    dut.i_instr.value = 0x0000000000000000
    dut.i_en.value = 0b0
    dut.i_i_form.value = 0b0
    dut.i_b_form.value = 0b0
    dut.i_cond_LR.value = 0b0
    dut.i_cond_CTR.value = 0b0
    dut.i_cond_TAR.value = 0b0

    dut.i_condition_register.value = 0x00000000
    dut.i_target_address_register.value = 0x0000000000000000

    await Timer(200, units="ps")  # reset counters
    dut.i_rst.value = 0b0
    await Timer(200, units="ps")  # reset counters
    await Timer(200, units="ps")  # reset counters
