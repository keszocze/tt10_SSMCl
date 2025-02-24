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

async def streaming_testcase(dut, width, mul_select_bits, debug=False):
        dut._log.info(f"Start test case for {width} bits\n")

        enable_bit = "1"
        # TODO compute the fill range?
        for x in range(0,10):
            for y in range(0,10):
                xS = myBin(x,width)
                yS = myBin(y,width)
                pS = myBin(x*y,2*width)
                dut._log.info(f"Testing {x}({xS}) * {y}({yS}) = {x*y}({pS})  ({width} bit, Streaming)")
                dut._log.info(f"{clkCounter}: Start streaming in")
                for i in range (0,width):
                    streamInIntString = mul_select_bits + enable_bit + xS[7-i] + yS[7-i]
                    streamInInt = int(streamInIntString.lstrip('0'),2)
                    dut._log.info(f"{clkCounter}: Setting to {streamInInt}({streamInIntString})")
                    dut.uio_in.value = streamInInt
                    await myTick(dut,1)

                
                dut.uio_in.value = 0
                dut._log.info(f"{clkCounter}: Waiting for the computation to finish")
                for i in range (0, (width*width)+1):
                    await myTick(dut, 1)
                    outS = myBin(dut.uio_out.value,width)
                    dut._log.info(f"{clkCounter}: {outS}")
                                
                
                #dut._log.info(f"{clkCounter}: Advance for debugging")
                #for i in range(0,3):
                #    await myTick(dut, 1)
                #    outS = myBin(dut.uio_out.value,width)
                #    dut._log.info(f"{clkCounter}: {outS}")

                dut._log.info(f"{clkCounter}: Starting to read out the values")
                for i in range(0,2*width):
                    outS = myBin(dut.uio_out.value,width)
                    dut._log.info(f"{clkCounter}: {outS}")
                    assert outS[0] == '1'
                    assert outS[1] == pS[((2*width)-1)-i]
                    await myTick(dut,1)


                # wait just to ensure that we finished streaming
                await myTick(dut,5)


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

    #for x in range(0,8):
    #    for y in range(0,8):
    #        dut._log.info(f"Testing {x} * {y} (3 bit, Int)")

            #startMulInputS = "10" + myBin(x) + myBin(y)
            #startMulInput = int(startMulInputS,2)

            #endMulS = "10" + myBin(x*y,6)
            #endMul = int(endMulS, 2)

            #dut.ui_in.value = startMulInput

            #await ClockCycles(dut.clk, 1)
            #dut.ui_in.value = 0
            
            #await ClockCycles(dut.clk,17)
                
            #assert dut.uo_out.value == endMul

            # idle a couple of clock cykles
            #await ClockCycles(dut.clk,4)

    await streaming_testcase(dut,8, "0")            
    await streaming_testcase(dut,16, "1")




    #for x in [0,67,564]:
    #    for y in [1,2,676]:
    #        xS = myBin(x,16)
    #        yS = myBin(y,16)
    #        pS = myBin(x*y,32)
    #        dut._log.info(f"Testing {x}({xS}) * {y}({yS}) = {x*y}({pS}) (16 bit, Streaming)")
    #        for i in range (0,16):
    #            streamInInt = int("11" + xS[7-i] + yS[7-i],2)
    #            #dut._log.info(f"Setting to {streamInInt}")
    #            dut.uio_in.value = streamInInt
    #            await ClockCycles(dut.clk,1)
    #            #clkCounter +=1
    #        
    #        dut.uio_in.value = 0
    #        await ClockCycles(dut.clk,257)
    #        #clkCounter+=65
    #        
    #        
    #        for i in range(0,32):
    #            outS = myBin(dut.uio_out.value,16)
    #            #dut._log.info(f"{clkCounter}: {outS}")
    #            assert outS[0] == '1'
    #            assert outS[1] == pS[15-i]
    #            await ClockCycles(dut.clk,1)
    #            #clkCounter+=1

#            # wait just to ensure that we finished streaming
#            await ClockCycles(dut.clk,5)            
            