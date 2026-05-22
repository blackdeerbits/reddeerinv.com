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
