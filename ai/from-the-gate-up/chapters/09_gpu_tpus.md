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
