# Chapter 2: The Hidden City of Data Movement

## The Mux You Never Think About

Now that we have our multiply-accumulate circuit — 16 AND gates and 16 full adders, a neat little package — we need to use it. That means connecting it to memory, feeding it numbers, and storing the results.

This is where the costs explode.

Picture a simple processor core. It has a register file — a small, fast local memory — with, say, eight entries, each holding a four-bit number. It has one multiply-accumulate unit. To perform one MAC, the core needs to grab three numbers from the register file (two inputs and one accumulator), feed them into the MAC, and write the result back.

How do you select which three of the eight registers to read? You use a circuit called a **multiplexer**, or mux for short.

A mux is a selector. It takes multiple inputs and, depending on a control signal, passes one of them through. You never see it. Your code never mentions it. But it is there, physically present on the chip, consuming area and power for every single register read.

## What a Mux Actually Costs

To build an 8-input mux for a 1-bit signal, you AND each of the eight inputs with a mask that says "is this the one I want?" and then OR all the masked results together. That's 8 AND gates and 7 OR gates — 15 gates total. For p bits, multiply by p. For our 4-bit case, that's 32 AND gates plus 28 OR gates.

And you need **three** muxes — one for each input to the MAC. That's 96 AND gates just for data movement.

Compare that to the MAC itself: 16 AND gates plus 16 full adders. The full adder, being a larger gate, costs more area than a single AND, but even accounting for that, the data movement circuitry is **many times more expensive** than the computation.

In this toy example, seven-eighths of the chip area is spent on moving data. Only one-eighth is spent on actual math.

## The Problem of the Register File

This ratio gets worse as the register file gets larger. A CPU might have hundreds of registers. A CUDA core might have thousands. Every additional register means a larger mux, which means more gates. The relationship is linear — double the registers, double the mux cost — but the compute unit doesn't grow at all. The same MAC, the same gate count, handling more and more overhead.

This is the hidden tax of general-purpose processors. They spend an enormous fraction of their silicon on flexibility — on the ability to read any register, operate on any data, handle any instruction. That flexibility is paid for in gates, and those gates don't do computation.

## The Pre-Volta World

Before NVIDIA introduced Tensor Cores in the Volta architecture (2017), every CUDA core used exactly this design. Each core had its own register file, its own muxes, its own small ALU. Programs could issue arbitrary instructions and read any register they wanted. The software was maximally flexible.

The hardware was maximally inefficient.

The ratio of data-movement gates to compute gates was so lopsided that most of the chip was doing nothing useful at any given moment. The cores were small, the register-file overhead large, and the amount of actual multiply-accumulate happening per square millimeter of silicon was pathetically low.

Something had to change. The change was the systolic array.
