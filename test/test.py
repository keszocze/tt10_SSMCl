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

async def streaming_testcase(dut, width, mul_select_bits, rngX, rngY, debug=False):
        dut._log.info(f"Start test case for {width} bits\n")

        enable_bit = "1"
        # TODO compute the fill range?
        for x in rngX:
            for y in rngY:
                xS = myBin(x,width)
                yS = myBin(y,width)
                pS = myBin(x*y,2*width)
                dut._log.info(f"Testing {x}({xS}) * {y}({yS}) = {x*y}({pS})  ({width} bit, Streaming)")
                if debug:
                    dut._log.info(f"{clkCounter}: Start streaming in")
                for i in range (0,width):
                    streamInIntString = mul_select_bits + enable_bit + xS[(width-1)-i] + yS[(width-1)-i]
                    streamInInt = int(streamInIntString.lstrip('0'),2)
                    if debug:
                        dut._log.info(f"{clkCounter}: Setting uio_in={streamInInt}({streamInIntString})")
                    dut.uio_in.value = streamInInt
                    await myTick(dut,1)

                
                #if mul_select_bits == "0":
                #    dut.uio_in.value = 0
                #else:
                dut.uio_in.value = int(mul_select_bits + "000",2)
                
                if debug:
                    dut._log.info(f"{clkCounter}: Waiting for the computation to finish")
                    for i in range (0, (width*width)+1):
                        outS = myBin(dut.uio_out.value,8)
                        dut._log.info(f"{clkCounter}: uoi_out={outS} / {myBin(dut.uio_in.value,8)}")
                        await myTick(dut, 1)
                else:
                    await myTick(dut, (width*width)+1)
                                

                if debug:
                    dut._log.info(f"{clkCounter}: Starting to read out the values")
                for i in range(0,2*width):
                    outS = myBin(dut.uio_out.value,width)
                    dut._log.info(f"{clkCounter}: uoi_out={outS} / {myBin(dut.uio_in.value,8)}")
                    #assert outS[0] == '1'
                    #assert outS[1] == pS[((2*width)-1)-i]
                    await myTick(dut,1)


                # wait just to ensure that we finished streaming
                if debug:
                    dut._log.info(f"{clkCounter}: Just add some cycles at the end for good measure")
                await myTick(dut,5)


async def int_testcase(dut):
    for x in range(0,8):
        for y in range(0,8):
            dut._log.info(f"Testing {x} * {y} (3 bit, Int)")

            startMulInputS = "10" + myBin(x) + myBin(y)
            startMulInput = int(startMulInputS,2)

            endMulS = "10" + myBin(x*y,6)
            endMul = int(endMulS, 2)

            dut.ui_in.value = startMulInput

            await ClockCycles(dut.clk, 1)
            dut.ui_in.value = 0
            
            await ClockCycles(dut.clk,17)
                
            assert dut.uo_out.value == endMul

            # idle a couple of clock cykles
            await ClockCycles(dut.clk,4)

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

    # TODO anscheinend habe ich einen off-by-one Fehler in der Dauer der Berechnungen?

    await streaming_testcase(dut, 2, "000", [2], [3], True)
    #await streaming_testcase(dut, 3, "001", range(0, 8), range(0, 8), True)
    #await streaming_testcase(dut, 4, "010", range(0,16), range(0,16), True)
    #await streaming_testcase(dut, 5, "110", range(0,32), range(0,32), True)
    await streaming_testcase(dut, 8, "100", [2], [3], True)            
    #await streaming_testcase(dut,10, "101", range(0, 8), range(0, 8), True)
    #await streaming_testcase(dut,12, "110", range(0, 8), range(0, 8), True)
    #await streaming_testcase(dut,16, "111", range(0, 8), range(0, 8), True)