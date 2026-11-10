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
| `mini-reef.kicad_sym` | Project symbols: CH347T, W958D8NBYA HyperRAM |
| `fp-lib-table`, `sym-lib-table` | Register the project libraries |

## Schematic sections

| # | Section | Main parts |
|---|---|---|
| 1 | USB-C & Power | USB-C, fuse, 3x TPS62130A (1.0 / 1.8 / 3.3 V, sequenced) |
| 2 | FPGA Power | XC7A15T unit D, UG483 decoupling |
| 3 | HyperRAM | W958D8NBYA5I on bank 35 (1.8 V), debug pins on bank 34 |
| 4 | USB-JTAG & Console | CH347T (mode 3), JTAG header, bank 0 config straps |
| 5 | Clock & Config | 50 MHz oscillator, W25Q32 flash, banks 14/15 |
| 6 | Test Host & Debug | CH32V307 link header, debug header, LEDs, button |
