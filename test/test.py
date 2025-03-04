# SPDX-FileCopyrightText: © 2024 Tiny Tapeout, 2025 Technical University of Denmark
# SPDX-License-Identifier: Apache-2.0
# This version was developed by Oliver Keszocze, DTU Compute, Embedded System Engineering
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


clkCounter = 0


def myBin(val, minLen=3):
  valS = bin(val)[2:]

  while len(valS) < minLen:
    valS = "0" + valS

  return valS

async def myTick(dut, n=1):
    await ClockCycles(dut.clk,n)
    global clkCounter
    clkCounter += n

async def int_testcase(dut):
    lastResult = 0
    for x in range(0,8):
        for y in range(0,8):
            dut._log.info(f"Testing {x} * {y} (3 bit)")

            startMulInputS = "10" + myBin(x) + myBin(y)
            startMulInput = int(startMulInputS,2)

            endMulS = "10" + myBin(x*y,6)
            endMul = int(endMulS, 2)

            dut.ui_in.value = startMulInput

            await myTick(dut,1)
            dut.ui_in.value = 0
            
            # hier dann eventuell in computing / streaming teilen
            for i in range(0,12):
                assert dut.uo_out.value == lastResult
                dut._log.info(f"{clkCounter}: computing the result (out={dut.uo_out.value})")
                await myTick(dut,1)
            for i in range(0,5):
                assert dut.uo_out.value == 0
                dut._log.info(f"{clkCounter}: streaming the result (out={dut.uo_out.value})")
                await myTick(dut,1)
            
            dut._log.info(f"{clkCounter}: should have result (out={dut.uo_out.value})")
            assert dut.uo_out.value == endMul

            lastResult = endMul

            # idle a couple of clock cykles
            await myTick(dut,4)

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")
    #clkCounter = 0


    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await myTick(dut,10)
    
    #clkCounter+=10
    dut.rst_n.value = 1

    dut._log.info("Test SSMCl behavior")

    await myTick(dut,1)


    assert dut.uo_out.value == 0

    await int_testcase(dut)

