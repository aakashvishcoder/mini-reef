# Mini-Reef FPGA Board

A low-cost 4-layer Artix-7 board that runs a small Reef-style accelerator against real HyperRAM, and measures bandwidth, latency and tokens per second. A CH32V307 board acts as the test host.

- FPGA: XC7A15T-FTG256 (footprint-compatible with XC7A35T)
- Memory: Winbond W958D8NBYA5I, 256 Mb HyperRAM on a 1.8 V bank
- USB-C: power, plus CH347T for USB-JTAG and console
- Manufacturing: JLCPCB 4-layer, assembled

## Layout

| Path | Contents |
|---|---|
| `schematic-guide/` | Section-by-section schematic guides |
| `planning-BOM.csv` | Planning BOM with LCSC numbers (not the JLC upload format) |
| `mini-reef.pretty/` | Project footprints not in KiCad's stock library |
| `fp-lib-table` | Registers the project footprint library |
