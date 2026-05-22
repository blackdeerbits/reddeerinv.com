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
