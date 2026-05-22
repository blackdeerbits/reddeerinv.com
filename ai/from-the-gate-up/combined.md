---
title: "From the Gate Up"
author: "the_red_deer"
date: "May 2026"
language: en
rights: CC BY 4.0
...
# Introduction: The Chip in Your Hands

You are reading these words on a device that contains billions of switches. Each switch is smaller than a virus. They flip on and off a billion times per second. Together, they make this text appear, the network fetch happen, the pixels render — and, increasingly, they power the AI models that are reshaping the world.

This is a book about those switches. Not about what chips do — everyone knows what chips do — but about *how they do it*. About the physical reality inside the silicon, the constraints that shape every decision in the AI industry, and the surprising elegance of what happens when you start from the very bottom and build up.

The standard way to learn about chips is top-down. Here is a CPU. Here is a GPU. Here is a TPU. Here is what each one is good at. This book does the opposite. We start with a single logic gate — the simplest possible circuit, a thing that takes two bits and produces one — and we stack, connect, and scale our way up until we can see why every chip in the world looks the way it does.

Why work bottom-up? Because the top-down view hides the most important fact about modern chips: almost all of their area, energy, and complexity is spent on moving data, not on computing. A \$30,000 GPU spends 90 percent of its transistors just shuffling numbers from one place to another. The actual math happens in a tiny fraction of the silicon. Every design decision in AI hardware — every trade-off, every innovation, every surprising benchmark number — traces back to this one asymmetry.

This book draws heavily on a conversation between Dwarkesh Patel and Reiner Pope, CEO of MatX, a new AI chip startup. Pope was a TPU architect at Google, and he walked through the entire stack from gates to GPUs on a blackboard. This book translates that conversation into a self-contained journey, adding context and narrative but never losing sight of the core insight: once you understand how a chip actually works, the entire AI industry makes more sense.

We start with the smallest thing. The AND gate.


# Chapter 1: The Multiply-Accumulate Machine

## The Universal Primitive

Inside every AI chip, the same operation happens billions of times per second. It is not a complicated operation. It is not a mysterious operation. It is the kind of arithmetic a third grader can do: multiply two numbers together, then add the result to a running total.

This is called a multiply-accumulate, or MAC for short. One MAC is trivial. A million MACs per second is a decent calculator. A billion MACs per second starts to look like intelligence.

The reason AI chips are designed around MACs is simple: matrix multiplication is just a giant pile of MACs. When a neural network runs, every neuron multiplies its inputs by weights and adds them together. That loop — `output[i][k] += input[i][j] × weight[j][k]` — is a MAC at every step. A modern AI training run might execute a billion billion of them.

## How a MAC Works at the Gate Level

A four-bit multiply-accumulate looks like this.

First, the multiplication. To multiply a four-bit number by another four-bit number, you do what you learned in elementary school: long multiplication, but in binary. Every bit of one number gets AND-ed with every bit of the other number. For a 4×4 multiply, that's 16 AND gates, each producing one partial product.

A single AND gate is almost the simplest thing you can build on a chip. Two inputs, one output — the output is 1 only if both inputs are 1. It is one of the primal building blocks that chip designers get from the foundry. It costs almost nothing in area and almost nothing in power.

Then comes the hard part: summing up the partial products. A four-bit multiply produces 16 partial product bits. Plus, you have the eight bits you're going to accumulate into. That's 24 bits that need to be collapsed down to eight bits — the final accumulated result.

You could sum them column by column, carrying bits the way a human would. But that's slow and inefficient. Instead, chip designers use a tool called a **full adder**, also known as a 3→2 compressor.

## The Full Adder

A full adder takes three single-bit inputs — all from the same column position — and produces two bits of output: a sum bit and a carry bit. If you feed it 1, 0, and 1, it outputs 10 (binary for 2). If you feed it 1, 1, and 1, it outputs 11 (binary for 3). It's essentially just counting and expressing the result in binary.

The magic of the full adder is that it eliminates one bit from the column every time you use it. You start with three bits in a column; you end with two bits (the sum goes in the same column, the carry goes into the next column over). The height of the column shrinks.

Apply full adders to every column, over and over, and the whole grid of partial products gradually collapses. Three bits become two. Two bits become one. When every column has exactly one bit, you're done. The remaining bits are your answer.

The number of full adders required? For a p-bit by q-bit multiply-accumulate, it's exactly p × q. In our 4×4 case, that's 16 full adders.

## The Quadratic Insight

This is where it gets interesting.

The total cost of the multiply-accumulate circuit scales as the **product** of the two bit widths. Halve the bit width of both operands — go from 8×8 to 4×4 — and the circuit shrinks by a factor of **four**, not two.

This is the quadratic scaling of precision, and it is the single most important fact about low-precision arithmetic. It is why neural networks can run so much faster at FP4 than FP8. It is why the industry is racing to lower and lower precision. It is not a linear improvement — it is a quadratic one.

Historically, NVIDIA reported that every time you halved precision, you doubled the FLOP count. That was a conservative claim. The gate-level math says the improvement should be closer to 4× for a true integer multiply. The real ratio is slightly less for floating-point (exponents add overhead), which is why NVIDIA's B300+ now reports FP4 at 3× FP8 rather than 2× — they have acknowledged the quadratic effect.

This scaling law is the engine behind the entire low-precision revolution. Every model quantization technique, every FP4 training paper, every claim about "same accuracy at half the bits" — they all bank on this one physical fact: smaller numbers mean quadratically less hardware.


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


# Chapter 3: The Amortization Trick

## Why Systolic Arrays Changed Everything

The insight behind the systolic array is simple: if you can't reduce the cost of moving data, increase the amount of computation you do per move.

A single multiply-accumulate requires three register reads. A 100×100 matrix multiplication requires 1,000,000 multiply-accumulates — but the data for the weight matrix can be loaded **once** and reused across the entire computation. The trick is to make the weight matrix live inside the compute unit itself, skipping the register file entirely for repeated accesses.

This is the systolic array: a grid of multiply-accumulate units, each with its own small local storage. The weight matrix is loaded into these local storages slowly, once, at startup. Then input vectors flow through the grid from one side, partial sums accumulate as they go, and output vectors emerge at the bottom.

## The Math of Amortization

Consider a systolic array of size X×Y. It performs X×Y multiply-accumulates per cycle. The data that needs to cross the boundary from the general-purpose register file: Y inputs per cycle (the vector) and X outputs per cycle (the partial sums). That's X+Y data movements.

The ratio: (X×Y) computations per (X+Y) data movements.

If X and Y are both 128 (the size of a first-generation TPU matrix unit), that's 16,384 computations per 256 data movements — a ratio of 64:1. Compare this to the original CUDA core design, where each MAC required three data movements and the ratio of compute to data movement was 1:3 (in favor of data movement). The improvement is dramatic.

## Two Key Optimizations

The systolic array exploits two things:

**Spatial reuse.** The weight matrix stays in place. Once loaded, a single weight participates in every dot product that passes through its row. The chip doesn't re-read it from memory, doesn't re-select it from a register file, doesn't waste a single gate on fetching it again. It just sits there, in a tiny local register, waiting for the next input to arrive.

**Slow loading.** The initial load of the weight matrix happens over many clock cycles, using minimal bandwidth per cycle. The data is trickle-fed into the systolic array through a daisy chain: on the first cycle, the first row loads; on the second cycle, the first row shifts down and the second row loads. The process is slow, but since weights are loaded only once for many computations, the speed of loading doesn't matter. What matters is the bandwidth of the loading — the number of wires crossing the boundary — and that stays small.

## The Trade-Off

Nothing is free. The systolic array trades flexibility for efficiency.

A general-purpose CUDA core can do any operation on any data. A systolic array can only do matrix multiplication. If your workload is matrix multiplication (and for neural networks, it overwhelmingly is), this is the right trade-off. If your workload is anything else, the systolic array is oversized and inflexible.

This is why modern GPUs have both: a grid of Tensor Cores (systolic arrays) for the matrix math, surrounded by general-purpose CUDA cores for everything else. The chip says "I know what you mostly do, and I optimized for that, but I kept the old stuff around just in case."

## The Sizing Decisions

Every chip designer faces the same question: how big should the systolic array be?

A bigger array means better amortization — more compute per data movement. But a bigger array also means more area, more power, and less flexibility. If the array is 256×256, it's extremely efficient for large matrix multiplies but wasteful for small ones (where most of the hardware sits idle).

This sizing question, this compute-versus-communication trade-off, shows up at every level of chip design. We saw it in the precision choice (quadratic vs. linear scaling). We see it here in the systolic array size. We'll see it again in chip-to-chip communication — the same principle, just at a different scale.

The decision is never obvious. That's why chip design is hard.


# Chapter 4: The Great Synchronization

## Why a Chip Needs a Heartbeat

A modern chip contains billions of transistors. They are all working simultaneously, computing different things, connected by a mesh of wires so dense that a single chip contains miles of routing. The obvious question: how does it all stay coordinated?

The answer is the clock cycle. Every nanosecond or so, every register on the chip pauses, stores its current value, and prepares for the next operation. The entire chip advances in lockstep, like soldiers marching.

This synchronization is not optional. Without it, signals would race ahead of each other, computations would mix data from different operations, and the chip would produce garbage. Every chip designer must ensure that between any two clock ticks, every computation path has enough time to finish — but not so much time that the clock speed suffers.

## The Critical Path

The maximum clock speed of a chip is determined by its slowest logic path. This is called the **critical path** — the chain of gates that takes the longest to compute. If the critical path takes 1 nanosecond, the chip can run at 1 GHz. If it takes 2 nanoseconds, the chip runs at 500 MHz.

Chip designers spend enormous effort shortening the critical path. They insert **pipeline registers**: intermediate storage points that break a long logic chain into shorter segments.

Picture a long chain of gates producing a result. On its own, it might take 2 nanoseconds — limiting the chip to 500 MHz. Insert a register in the middle, and now you have two chains of 1 nanosecond each. The clock can run at 1 GHz, twice as fast. The cost: an extra register, which takes area and power, plus the latency of passing through the register.

## The Pipeline Trade-Off

This is the fundamental trade-off of pipelining:

- **More pipeline stages** → faster clock, more parallelism, but more registers and higher latency.
- **Fewer pipeline stages** → slower clock, less area in registers, lower latency.

Pushing pipeline registers in too aggressively is the equivalent of building a factory where every workstation is a micro-kitchen — the overhead of the workstations themselves consumes most of the budget. Going too far means you spend almost all your area on synchronization and almost none on actual computation.

This trade-off appears throughout chip design. It exactly mirrors the batch-size dilemma from data-center economics: smaller batches (shorter pipelines) give each individual request lower latency, but the total throughput of the system goes down because the overhead per operation dominates.

## The Feedback Loop Problem

Pipelining is straightforward when data flows in one direction — in, through the pipeline, out. It becomes much harder when computation loops back on itself.

Consider a simple accumulation: `sum = sum + input`. On every clock cycle, a new input arrives and gets added to the running total. This is a feedback loop — the output of the adder feeds back into one of its inputs on the next cycle.

If the addition takes too long, you cannot insert a pipeline register in the middle without breaking the computation. A register would split the addition into two parts, but the second part would get the wrong value — it would receive the previous cycle's partial result instead of the current cycle's. The accumulation would compute even-cycle sums and odd-cycle sums separately, never combining them.

This feedback constraint — loops in the logic — sets the real clock speed of most chips. No amount of pipelining can eliminate it, because some operations inherently need their own result to make progress.

## The Throughput-Latency Mirror

There is a deep parallel here to how data centers operate, and it is worth pausing on.

Pope drew this connection explicitly. A chip's pipelining problem — do you optimize for low latency (few pipeline stages) or high throughput (many pipeline stages)? — is structurally identical to a server's batching problem — do you optimize for response time (small batches) or total throughput (large batches)?

The same physics appears at every scale. The chip waits for its clock cycle to complete. The server waits for its batch to fill. The data center waits for its interconnect to deliver data. The constraint is always the same: you can have fast individual operations, or you can have many operations per second, but you cannot have both.

This is why the waiting game, as described in the earlier books in this series, is not a temporary quirk of AI hardware. It is a fundamental property of computation itself.


# Chapter 5: The Flexible Frankenstein

## What an FPGA Actually Is

An ASIC (Application-Specific Integrated Circuit) is a chip designed for one purpose. A GPU is an ASIC for graphics. A TPU is an ASIC for matrix multiplication. Every gate, every wire, every transistor is laid out permanently. You cannot change it after manufacturing.

An FPGA (Field-Programmable Gate Array) is the opposite: a chip whose logic can be rewired after it leaves the factory. You buy one chip and configure it to be an Ethernet switch, a signal processor, a financial trading engine, or anything else — changing the configuration takes milliseconds.

This programmability comes at a massive cost. An FPGA is roughly **10× less area-efficient and 10× more power-hungry** than an equivalent ASIC. Every design decision in an FPGA is a compromise between flexibility and efficiency.

## How an FPGA Works

An FPGA contains three basic building blocks:

**Lookup tables (LUTs).** A LUT is a small programmable truth table. A typical LUT has four inputs and one output. The 16 possible input combinations map to 16 stored bits, which the designer sets to implement any four-input logic function — AND, OR, XOR, NAND, anything. The LUT is essentially a big mux: given four address bits, it selects one of 16 stored values.

**Registers.** Small storage elements that hold one bit each, providing the memory elements for stateful logic.

**Routing muxes.** These are the key to programmability. Every LUT input is preceded by a mux that selects which nearby signal to use. Every LUT output feeds into a mux that connects it to the rest of the chip. Programming an FPGA means configuring every single one of these muxes — telling each one which signal to pass through.

## Muxes All the Way Down

Here is where the cost becomes clear.

A four-input LUT is a mux with 16 inputs. As we established in Chapter 2, an n-input mux costs n AND gates plus n-1 OR gates. A 16-input mux costs 16 ANDs plus 16 ORs — 32 gates. This single LUT, which implements one gate's worth of logic, costs 32 gate-equivalents in overhead.

The routing muxes in front of every LUT add even more. To select from eight nearby signals, each input mux costs 8 ANDs plus 7 ORs per bit. Multiply by four inputs per LUT, and the routing overhead dwarfs the logic.

Compare this to an ASIC, where implementing a 4-input AND gate costs exactly three AND gates — no muxes, no lookup table, no programmability overhead. The FPGA pays a 10× tax for the privilege of being reconfigurable.

## The Business Case

This tax determines where FPGAs make sense versus ASICs.

The first ASIC costs \$30 million to manufacture. The mask set, the wafer runs, the packaging, the testing — all upfront. If you plan to sell a million units, the per-chip cost is $30 plus the silicon. If you plan to sell ten units, the per-chip cost is $3 million each.

The first FPGA costs \$10,000. You buy it off the shelf. The per-chip cost is nearly the same whether you buy one or a million.

So FPGAs win when:
- **Volume is low** (defense, aerospace, research)
- **The workload changes** (financial trading models updated weekly)
- **Latency is critical** (high-frequency trading — FPGAs provide deterministic, sub-microsecond processing)

ASICs win when:
- **Volume is high** (data center GPUs sell hundreds of thousands)
- **The workload is stable** (matrix multiplication isn't changing)
- **Efficiency matters** (every watt in a data center costs real money)

## The Architecture Is Not the Point

The deeper lesson of the FPGA is that chip design is always about the same trade-off. Every decision — whether to use an FPGA or an ASIC, a big systolic array or a small one, FP4 or FP8 — boils down to the same question: are you optimizing for the general case or the specific one?

The FPGA chooses maximum generality. It pays the full flexibility tax. The ASIC chooses maximum specialization. It gets maximum efficiency but can only do one thing.

Everything else is somewhere on that spectrum.


# Chapter 6: The Two Kinds of Memory

## The Cache Gamble

Every general-purpose processor faces a problem. The main memory (DRAM) is fast enough for storage but far too slow for the processor's needs — roughly 100× slower than the processor's clock speed. Without a solution, the processor would spend almost all its time waiting for memory.

The solution is the **cache**: a small, fast memory that sits between the processor and main memory, automatically storing recently accessed data. When the processor asks for a piece of data, the cache checks whether it has a copy. If it does (a cache hit), the data arrives in a few nanoseconds. If it doesn't (a cache miss), the processor stalls for a hundred nanoseconds while the data is fetched from main memory.

This system works remarkably well for most software. Programs tend to access the same data repeatedly (temporal locality) and data that lives nearby (spatial locality). The cache exploits both patterns, and average access times drop dramatically.

But there is a hidden cost: non-determinism. Whether a particular memory access hits or misses the cache depends on the chip's entire history — what other programs ran, what data they accessed, how the cache replacement policy made its decisions. The same instruction, with the same data, can take 2 nanoseconds or 100 nanoseconds depending on ambient state.

For most applications, this variability doesn't matter. For high-frequency trading, real-time control systems, and other latency-sensitive workloads, it is catastrophic.

## The Scratchpad Alternative

An alternative approach exists, and it is the one used by TPUs and many AI accelerators: the **scratchpad**.

Instead of a hardware-managed cache, the chip has a small, fast memory that is **software-managed**. The program decides explicitly what goes into the scratchpad and when. There are separate instructions for accessing the scratchpad (fast, deterministic) and for accessing main memory (slow, but you know it will be slow).

This eliminates non-determinism entirely. If you write to the scratchpad, the data is there. If you want to bring data from main memory, you issue an explicit DMA command, and the chip waits until it completes. There are no cache misses, no replacement policy surprises, no variability.

The cost is programmability. The software must explicitly manage data movement, deciding what to load, when to load it, and when to evict it. This is harder to program than a cache, where the hardware handles everything automatically. But for workloads like neural network inference, where the data access pattern is known in advance (every layer loads its weights, processes a batch, and produces outputs), the scratchpad is simple and efficient.

## Why It Matters for AI

The cache-versus-scratchpad decision illustrates something deeper about the AI hardware ecosystem.

A GPU uses caches because it is designed for graphics workloads first, and graphics (like general-purpose computing) benefits from automatic caching. The cache made sense for CUDA cores running arbitrary shader programs.

A TPU uses scratchpads because it is designed for matrix multiplication, and matrix multiplication has a known, predictable memory access pattern. The scratchpad eliminates cache hardware (saving area and power) and eliminates cache-miss stalls. Every operation takes exactly as long as the programmer expects.

This is not a technical debate about which is better. It is a design choice shaped by the intended workload. GPU designers optimize for flexibility; they accept the overhead of cache management. TPU designers optimize for determinism and efficiency; they accept the programming burden of explicit data movement.

Both approaches work. The question is not "which is right" but "what are you trying to optimize for?" — and the answer, in AI chips, is shifting increasingly toward determinism as the workload stabilizes.


# Chapter 7: The Bloat of Brains

## The CPU: A General-Purpose Machine

A modern CPU is a marvel of engineering. It handles web browsers, operating systems, spreadsheets, video games, and dozens of other workloads simultaneously, switching between them so fast that the user never notices. This versatility is the CPU's defining feature.

It is also the source of its inefficiency.

A CPU core uses a large fraction of its die area for things that have nothing to do with computation:

**The branch predictor.** When a program encounters an `if` statement, the CPU doesn't know which branch will be taken until the condition is evaluated. But evaluating the condition takes time — potentially several clock cycles. The CPU wants to keep executing during those cycles, so it **predicts** which branch will be taken and starts executing speculatively. If the prediction is wrong, it discards the results and starts over.

This prediction is not trivial. Modern branch predictors use sophisticated pattern matching, tracking the history of every branch to anticipate its behavior. All of this takes area — a substantial amount of it.

**The out-of-order execution engine.** A CPU does not execute instructions in the order they appear. It reorders them to keep its execution units busy, dynamically scheduling work across multiple integer units, floating-point units, load/store units, and vector units. The hardware that manages this reordering — the reservation stations, reorder buffer, register renaming tables — consumes enormous area.

**The large register file.** A CPU needs many registers to support multiple in-flight instructions. Each register adds to the mux overhead we discussed in Chapter 2.

**Deep caches.** Three levels of cache, each larger and slower than the last, occupying significant die area.

The result: a single CPU core might consume 10-20 square millimeters of silicon at a modern process node. On that area, you could fit dozens or even hundreds of simpler cores.

## What a GPU Strips Out

The GPU takes a different approach. It removes almost everything that makes a CPU core general-purpose.

No branch predictor — or a very minimal one. GPU cores execute the same instruction on many data elements (SIMT, a variant of SIMD). If threads diverge (one takes a branch, another doesn't), both paths are executed serially, with the inactive threads masked out. This is less efficient for divergent workloads, but for predictable, massively parallel work (graphics, matrix math), it barely matters.

No out-of-order execution. GPU cores execute instructions in program order. They get parallelism from having many threads, not from reordering a single thread.

Simpler register files. GPU registers are smaller per thread, and the mux overhead is amortized across many threads.

Smaller caches — or scratchpads instead. GPUs rely on software-managed shared memory (which is a scratchpad) rather than hardware-managed caches for most workloads.

The result: a GPU can pack thousands of simple cores on the same die area that a CPU would use for a few dozen complex ones.

## The Performance Paradox

Here is the surprising thing: for workloads that fit the GPU's model, the simpler cores are faster. A GPU can achieve 10-100× the throughput of a CPU on matrix multiplication, even though its individual cores are much slower.

But for workloads that do not fit — serial code with unpredictable branches, pointer-heavy data structures, single-threaded tasks — the CPU's complexity pays off. Its branch predictor, out-of-order engine, and deep caches squeeze maximum performance from a single thread of execution.

This is why modern systems have both. The CPU handles the control flow, the operating system, the tasks that cannot be parallelized. The GPU handles the data-parallel work. The system works because each chip does what it is optimized for.

The question for the AI industry: as workloads stabilize around matrix multiplication, how much of the general-purpose complexity do we need? The answer, increasingly, is "less than we thought" — and that is driving the shift toward specialized AI accelerators.


# Chapter 8: The Wet Chip

## The Brain's Different Architecture

The human brain processes information, just like a chip. But the comparison ends quickly. The brain works on completely different principles.

A neuron fires at about 10-100 times per second. A modern chip runs at billions of cycles per second. The brain is a million times slower.

But the brain has roughly 100 billion neurons, each connected to thousands of others. The total number of synapses is in the hundreds of trillions. A chip might have 200 billion transistors, but each transistor is a simple switch, not an integrative computational unit like a neuron. The brain's parallelism is on a scale that silicon cannot touch.

## Why the Brain Is So Slow

Chip designers could make a chip run at a few megahertz instead of a few gigahertz. That would save enormous amounts of energy. Why don't they?

The answer is that chip energy is dominated by **switching power**. Every time a transistor transitions from 0 to 1 or back to 0, it charges or discharges a tiny capacitor. That charge-discharge cycle consumes energy. If you run the chip at a slower clock, fewer transitions happen per second, and energy drops proportionally.

But the brain is not slow because it saves energy. It is slow because biology is slow. A neuron's signaling relies on ion channels opening and closing, neurotransmitters diffusing across synapses, membrane potentials building up and discharging. These are electro-chemical processes, operating at biological time scales. You cannot speed them up without fundamentally changing the medium.

## Where the Brain Wins

Despite the clock-speed disadvantage, the brain wins on several fronts:

**Co-location of memory and compute.** In a chip, memory and compute are separate. Data must travel from the register file to the ALU and back — the movement cost we analyzed in Chapter 2. In the brain, the synapse is both memory and compute. The connection strength (weight) is stored at the connection point. Signal processing happens at the same physical location. There is no data movement cost.

**Unstructured connectivity.** A chip's wiring is planned, regular, and limited. Wires go where the layout designer put them, and they consume area that cannot be used for computation. The brain's connectivity is a three-dimensional tangled web. Neurons connect to other nearby neurons through dendrites and axons that grow in three dimensions, packing connectivity density far beyond what two-dimensional silicon lithography can achieve.

**Massive parallelism, individually slow.** The brain's 100 billion neurons are all computing simultaneously. Each one is slow, but there are so many of them that the total computation per second is staggering — estimates range from 10^15 to 10^18 operations per second. A modern GPU might achieve 10^15 operations per second for matrix multiply, but only for that specific operation. The brain can do general-purpose computation at similar throughput.

## The Energy Comparison

The human brain consumes about 20 watts. A modern GPU consumes 700 watts for a fraction of the general-purpose capability. The brain's energy efficiency is orders of magnitude higher.

Some of this gap is fundamental (biology wins on co-location and 3D connectivity). Some of it is architectural (the brain is an analog, stochastic computer, tolerant of errors and noise in ways that digital silicon is not). Some of it is just engineering maturity: we have been building chips for 70 years and brains for millions.

The gap may never close entirely for general-purpose intelligence. But for the narrow, specific computation that defines modern AI — matrix multiplication — silicon is already more efficient than biology. That is the bargain the industry has made: lose generality, gain speed.

## What It Means for AI Chips

The brain is not a model for how to build a better AI chip. Its architecture is constrained by biology in ways that silicon is not. But the brain does illustrate a principle that chip designers are rediscovering: the most efficient computation happens where the data lives.

This is the insight behind systolic arrays (Chapter 3), behind scratchpads (Chapter 6), and behind every effort to reduce data movement. The optimal chip looks less like a traditional processor — with its centralized register file and distant memory — and more like a brain: distributed, local, and specialized.

But it will not run at 10 Hz. It will run at 2 GHz, because it can, and because for the tasks we care about, speed still matters.


# Chapter 9: A Bunch of Tiny Everything

## The GPU-TPU Convergence

At the highest level, a GPU and a TPU are organized completely differently.

A GPU is a regular grid of almost-identical units called Streaming Multiprocessors (SMs). Each SM contains its own register file, its own warp scheduler, its own local memory, and a set of Tensor Cores. There are typically 100-200 SMs on a modern data-center GPU. They are connected by a shared L2 cache in the center of the chip.

A TPU is organized into coarse-grained blocks: a handful of very large matrix units (MXUs), a vector unit, and some local memory. A first-generation TPU had just two MXUs, each 128×128 systolic arrays. There are no SMs, no warp schedulers, no complex thread management.

But here is the insight: **a Tensor Core inside a GPU's SM is a tiny TPU.**

The architecture is the same. It is a systolic array with local storage, performing matrix-vector multiplication. The difference is scale. The TPU builds one very large instance and amortizes the control overhead across it. The GPU builds many small instances and amortizes the control overhead by running thousands of threads.

## The Trade-Off

Which approach is better? It depends on the workload.

A large systolic array (TPU style) is maximally efficient when the matrix multiplications are large. The amortization ratio is higher — more compute per unit of data movement overhead. But large matrices must be moved into and out of the array through a limited number of data paths, creating a bandwidth bottleneck.

Many small systolic arrays (GPU style) are more flexible. Each SM works independently, processing its own tile of the matrix. Data can be distributed across the SMs through many parallel paths — the L2 cache connects each SM to the others — so aggregate bandwidth is higher. But the overhead per SM (registers, scheduling, local memory) reduces the effective compute density.

The TPU design assumes large, regular matrix multiplications. The GPU design handles both large and small, regular and irregular, at the cost of lower peak efficiency.

## The Splittable Array

MatX, Reiner Pope's startup, has publicly discussed something called a **splittable systolic array**. The idea: construct a large systolic array that can also be partitioned into smaller independent arrays.

In large-MX mode, it acts like a TPU — maximum amortization, best efficiency for large matrix multiplies. In small-array mode, the hardware acts like a collection of smaller Tensor Cores — handling the smaller, irregular operations that a pure TPU struggles with.

This is the convergence. Not a GPU or a TPU, but something that can be either, depending on the workload. The chip says "I know you need both, so I built one thing that can do both."

## Why This Matters

The GPU-TPU convergence is not an academic debate about architecture. It is the leading edge of the inference economics discussed in earlier books.

If AI models stay large — think GPT-5 scale, 100 trillion parameters — large systolic arrays win. The amortization advantage is decisive. If models shrink, as quantization and distillation make smaller models more capable, small systolic arrays win. The flexibility advantage matters more.

A chip that can smoothly switch between the two modes is a hedge against uncertainty. It says: "I don't know what the frontier will look like three years from now, but I have designed something that works well either way."

That is the right posture for the current moment. The industry is evolving too fast for a permanent bet.


# Afterword: What "From the Gate Up" Teaches Us

We started with a single AND gate. Two inputs, one output. The simplest possible circuit. From that foundation, we built our way up through multiply-accumulate units, muxes, systolic arrays, pipeline registers, lookup tables, caches, and branch predictors — until we could see the entire shape of a modern AI chip and understand why it looks the way it does.

The journey reveals two things.

## The One Problem

Every design decision in chip architecture is a response to the same problem: moving data is expensive.

This truth appears at every level of the stack.

At the gate level, the muxes that select inputs from the register file cost more than the computation unit itself. The ratio is worse for larger register files, which is why specialized accelerators keep their local storage minimal.

At the architecture level, the systolic array exists specifically to amortize data-movement costs. It loads the weight matrix once and reuses it across thousands of computations, transforming a data-movement-heavy process into a compute-heavy one.

At the system level, the choice between cache and scratchpad is a choice about how much non-determinism you are willing to accept in exchange for automatic data movement. The choice between FPGA and ASIC is a choice between paying the flexibility tax once or paying it on every operation.

At the organizational level — the level of the data center — the same trade-off appears as the batch-size problem: do you optimize for latency (small batches, more data movement per computation) or throughput (large batches, less data movement per computation)?

Chip design is not a collection of unrelated specialties. It is the same optimization, applied at different scales.

## The One Question

The question that every chip designer faces, at every level, is the same: **how much flexibility are you willing to trade for efficiency?**

More flexibility means more muxes, more routing, more control logic, more overhead. Less flexibility means harder programming, narrower applicability, more risk if the workload changes.

The GPU chooses flexibility. It pays a heavy tax — the vast majority of its die is overhead — but it runs almost any workload.

The TPU chooses efficiency. It removes the overhead and gets more compute per square millimeter, but it only does matrix multiplication well.

The FPGA chooses extreme flexibility. It pays a 10× tax but can be rewired in the field for any digital circuit.

The brain chooses... something else entirely. It gets efficiency through co-location and 3D connectivity, speed through massive parallelism, and generality through a fundamentally different computational model.

## Where We Are Headed

The AI chip industry is converging on a compromise: chips that can be both efficient and flexible, depending on the moment. The splittable systolic array is one example. The trend toward programmable scratchpads, configurable precision, and reconfigurable data paths points in the same direction.

But the fundamental physics will not change. Data movement will always be expensive. The area and power costs of moving a bit across a chip will always exceed the cost of computing on it. Every future innovation — optical interconnects, 3D stacking, analog compute, neuromorphic architectures — is a bet on a different way to manage this cost.

Understanding the trade-off does not make it go away. But it makes the industry's decisions legible. When NVIDIA announces FP4 is 3× FP8, you know the quadratic scaling law behind it. When a startup claims its chip is 10× more efficient for inference, you know to ask: "What did you give up to get that efficiency, and does my workload fit?"

The waiting game that defined the last few years of AI — the memory wall, the bandwidth bottleneck, the idle compute units — is not going away. But understanding the full stack, from the gate to the chip, makes it possible to see where the bottlenecks are and what kind of innovation would break them.

Everything in this book traces back to a single AND gate and a simple question about how two bits combine. The rest is just the same idea, scaled up.


# Sources

This book draws heavily on the following source:

**"Reiner Pope — Chip design from the bottom up"** — Dwarkesh Podcast, May 22, 2026
- YouTube: https://youtu.be/oIk3R-sMX5o
- Transcript: https://www.dwarkesh.com/p/reiner-pope-2

Reiner Pope is the CEO of MatX, a new AI chip startup. He was previously at Google, where he worked on software efficiency, compilers, and TPU architecture.

## Related Books in This Series

- **The Waiting Game** — How Inference Economics Shapes the Future of AI. A journey through the memory wall, KV caches, batch economics, speculative decoding, and custom silicon.
- **Beyond the Waiting Game** — How AI is Learning to Work Around the Memory Wall. The sequel exploring what comes after inference economics — architectures and techniques that reshape how models think.
- **The Model That Does Everything** — What NVIDIA's Diffusion LM Means for Inference. A critical analysis of NVIDIA's Nemotron-Labs-Diffusion.

## Technical References

- Dadda, L. (1965). "Some schemes for parallel multipliers." *Alta Frequenza*, 34:349–356. — The standard Dadda multiplier architecture referenced in Chapter 1.
- Jouppi, N. P., et al. (2017). "In-Datacenter Performance Analysis of a Tensor Processing Unit." *ISCA 2017*. — The original TPU paper describing systolic array architecture.
- NVIDIA (2024). "NVIDIA B200 GPU Architecture Whitepaper." — FP4 performance claims discussed in Chapter 1.


