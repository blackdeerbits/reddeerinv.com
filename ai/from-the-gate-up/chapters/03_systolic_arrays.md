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
