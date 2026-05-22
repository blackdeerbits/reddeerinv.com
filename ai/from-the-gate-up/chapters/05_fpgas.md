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

The first ASIC costs $30 million to manufacture. The mask set, the wafer runs, the packaging, the testing — all upfront. If you plan to sell a million units, the per-chip cost is $30 plus the silicon. If you plan to sell ten units, the per-chip cost is $3 million each.

The first FPGA costs $10,000. You buy it off the shelf. The per-chip cost is nearly the same whether you buy one or a million.

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
