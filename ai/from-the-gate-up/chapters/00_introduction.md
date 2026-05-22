# Introduction: The Chip in Your Hands

You are reading these words on a device that contains billions of switches. Each switch is smaller than a virus. They flip on and off a billion times per second. Together, they make this text appear, the network fetch happen, the pixels render — and, increasingly, they power the AI models that are reshaping the world.

This is a book about those switches. Not about what chips do — everyone knows what chips do — but about *how they do it*. About the physical reality inside the silicon, the constraints that shape every decision in the AI industry, and the surprising elegance of what happens when you start from the very bottom and build up.

The standard way to learn about chips is top-down. Here is a CPU. Here is a GPU. Here is a TPU. Here is what each one is good at. This book does the opposite. We start with a single logic gate — the simplest possible circuit, a thing that takes two bits and produces one — and we stack, connect, and scale our way up until we can see why every chip in the world looks the way it does.

Why work bottom-up? Because the top-down view hides the most important fact about modern chips: almost all of their area, energy, and complexity is spent on moving data, not on computing. A $30,000 GPU spends 90 percent of its transistors just shuffling numbers from one place to another. The actual math happens in a tiny fraction of the silicon. Every design decision in AI hardware — every trade-off, every innovation, every surprising benchmark number — traces back to this one asymmetry.

This book draws heavily on a conversation between Dwarkesh Patel and Reiner Pope, CEO of MatX, a new AI chip startup. Pope was a TPU architect at Google, and he walked through the entire stack from gates to GPUs on a blackboard. This book translates that conversation into a self-contained journey, adding context and narrative but never losing sight of the core insight: once you understand how a chip actually works, the entire AI industry makes more sense.

We start with the smallest thing. The AND gate.
