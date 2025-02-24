![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) 
# The SSMCl project

This project contains multiple unsigned multipliers that have been developed using [Clash](http://www.clash-lang.org) and will be submitted to [TinyTapeout](https://tinytapeout.com/) shuttle number 10:

* Multiple multipliers exposing a streaming interface consisting of two input bits, one for each operand, and one start signal (2, 3, 4, 5, 8, 10, 12, and 16 bits) and
* a 3-bit version expecting two inputs in binary representation and a start signal for convenient use with the web interface of the TinyTapeout Development Kit

They are designed with minimality in mind at the expence of required cycles. For fun, the designs have been developed using the Clash language. As this is a proof-of-concept design also for learnign Clash, not much time and/or effort has been put into actually optimizing the design in any way.

### The general n-bit multiplier

The multiplier will compute the product $p = x \cdot y$ for $n$-bit inputs $x$ and $y$. The width of the output $p$ is $2\cdot n$.

The multiplier has three 1-bit inputs: a `start` signal and one signal for each input `x` and `y`. When `start` is asserted, the multiplier starts to stream in the values for $x$ and $y$ bit-wise; starting with the least significatn bit. The cycle in which `start` is asserted takes the least significant bits for $x$ and $y$ at `x` and `y`, respectively. The next $n-1$ cycles, the next bits of the operands should be made available at `x` and `y`.

When the operands are fully streamed, the multiplier begins its operation for $n\cdot n$ cycles. After the computation is finished, the $2\cdot n$ bits of the product are streamed back; least significant bit first.

At the $(3+n)\cdot n$'th cycle, the full product is stremed back.

Asserting `start` before the multiplication has been fully carried out does not have any effect on the circuit, i.e. the mulitplier is not interruptible.

### Multipliers in the design

The design features 8 multipliers of different bit-widths that can be selected by specifying setting the `mulSel` signal (see the pinout section below) to the values specified in the following table.

| Bit-with | Bit pattern |
|----------|-------------|
| 2        | 000         |
| 3        | 001         |
| 4        | 010         |
| 5        | 011         |
| 8        | 100         |
| 10       | 101         |
| 12       | 110         |
| 16       | 111         |

Note that the value of `mulSel` needs to be stable during the full operation of the multiplier as the input/output signals are routed to/from the wrong multiplier.

#### 2-bit Multiplier
The 2-bit multiplier is simply a specialization of the general n-bit multiplier as explained above. The select it, assert `mulSel=000` and use the other bidiretional ports as described in the table in the pinout section below.

The following wave trace shows the multiplication 
$2 \cdot 2 =  (10)_2  \cdot (11)_2 = 6 = (0110)_2$. 
To ease the reading, additional signals (`x'`, `y'`, `product'`) have been defined that show the low/high value as a number.

![full wave trace for the 2-bit multiplier](docs/streaming2.png)


#### 8-bit Multiplier
The 8-bit multiplier is simply a specialization of the general n-bit multiplier as explained above. The select it, assert `mulSel=100` and use the bidiretional ports as described in the table in the pinout section below.

The following abbreviated wave trace shows the multiplication 
$138 \cdot 86 =  (10101010)_2  \cdot (01010110)_2 = 11868 = (0010111001011100)_2$. 
To ease the reading, additional signals (`x'`, `y'`, `product'`) have been defined that show the low/high value as a number.

![abbreviated wave trace for the 8-bit multiplier](docs/streaming8.png)

### Convenient 3-bit Multiplier
The 3-bit multiplier exposes a human friendly interface by accepting integer values as input, i.e. it wraps the general multiplier as described above. When `start` is asserted, the values at the `x` and `y` inputs are then being streamed into the actual multiplier, taking 3 cycles in total. The multiplier computes the product in 9 cycles and then steams back the 6-bit product in 6 cycles. The result can be seen at the output bit in cycle $18$. The result will remain valid until the next multiplication is started. Then abbreviated wave trace below illustrates this.

The bit-width has been chosen so that the multiplier can conveniently be used through the web interface of the TinyTapeout Development Kit.

![wave trace for the 3-bit multiplier](docs/int3.png)



## Verification
Both multipliers have been fed with all possible inputs, i.e. $64$ for the 3-bit multiplier and $65536$ for the 8-bit multiplier. The testbench is written in [cocotb](https://www.cocotb.org/) and can be found [here](test/test.py). For valid inputs, both multipliers are working correctly. 

What has not been tested is what happens when there are assertions of the `start` signal while a multiplication is still being carried out. Depending on your level of pedantry, you can consider these multipliers to be fully verified.