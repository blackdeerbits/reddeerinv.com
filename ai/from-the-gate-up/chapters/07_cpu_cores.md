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
