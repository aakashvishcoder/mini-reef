# Section 2: FPGA Power & Decoupling

**What it does:** feeds the FPGA's power pins and gives every rail the capacitors AMD requires. No signals here, just power.

Checked 2026-11-09 against AMD UG483 v1.14 (Table 2-2), DS181 v1.27.1 and UG470 v1.17.

**Sheet layout (all sections):** top row boxes `1 Power`, `2 FPGA Power`, `3 HyperRAM`; bottom row `4 USB-JTAG`, `5 Clock & Config`, `6 Test Host & Debug`.

## The FPGA symbol

| Ref | Value | Symbol | Footprint | LCSC | JLC type |
|---|---|---|---|---|---|
| U4 | XC7A15T-1FTG256C | `FPGA_Xilinx_Artix7:XC7A15T-FTG256` | `Package_BGA:Xilinx_FTG256` | C1521788 | Extended |

The symbol has **4 units**. Each one goes in a different section:

| Unit | Contents | Goes in |
|---|---|---|
| U4A | Banks 14 + 15 I/O | Section 5 |
| U4B | Banks 34 + 35 I/O | Section 3 |
| U4C | Bank 0: JTAG and configuration | Section 4 |
| **U4D** | **VCCINT, VCCBRAM, VCCAUX, GND, XADC power** | **This section** |

The symbol's Footprint field is empty, so set it to `Package_BGA:Xilinx_FTG256` yourself. The XC7A35T uses the same package and pinout, so this board takes either chip.

## Parts in this section

Capacitor counts are UG483 Table 2-2's FTG256 row for the **XC7A35T**, so the board works with either FPGA. I use **1µF 0402 instead of 0.47µF**: UG483 only requires at least 0.47µF, and 1µF is a free Basic part.

| Ref | Value | Footprint | LCSC | Rail |
|---|---|---|---|---|
| C13 | 100uF 6.3V 1206 | `Capacitor_SMD:C_1206_3216Metric` | C15008 | VCCINT |
| C14, C15 | 4.7uF 25V 0805 | `Capacitor_SMD:C_0805_2012Metric` | C1779 | VCCINT |
| C16, C17, C18 | 1uF 0402 | `Capacitor_SMD:C_0402_1005Metric` | C52923 | VCCINT |
| C19 | 47uF 10V 1206 | `Capacitor_SMD:C_1206_3216Metric` | C96123 | VCCBRAM |
| C20 | 1uF 0402 | `Capacitor_SMD:C_0402_1005Metric` | C52923 | VCCBRAM |
| C21 | 47uF 10V 1206 | `Capacitor_SMD:C_1206_3216Metric` | C96123 | VCCAUX |
| C22, C23 | 4.7uF 0805 | `Capacitor_SMD:C_0805_2012Metric` | C1779 | VCCAUX |
| C24, C25, C26 | 1uF 0402 | `Capacitor_SMD:C_0402_1005Metric` | C52923 | VCCAUX |
| C27 | 100nF 0402 | `Capacitor_SMD:C_0402_1005Metric` | C1525 | VCCADC |
| C28 | 47uF 1206 | `Capacitor_SMD:C_1206_3216Metric` | C96123 | VCCO_0 |
| C29 / C30, C31 / C32–C35 | 47uF / 4.7uF ×2 / 1uF ×4 | as above | C96123 / C1779 / C52923 | VCCO_14 |
| C36 / C37, C38 / C39–C42 | 47uF / 4.7uF ×2 / 1uF ×4 | as above | C96123 / C1779 / C52923 | VCCO_15 |
| C43 / C44, C45 / C46–C49 | 47uF / 4.7uF ×2 / 1uF ×4 | as above | C96123 / C1779 / C52923 | VCCO_34 |
| C50 / C51, C52 / C53–C56 | 47uF / 4.7uF ×2 / 1uF ×4 | as above | C96123 / C1779 / C52923 | VCCO_35 |

All capacitors here are **JLC Basic**, so no fees. Symbol: `Device:C` for all.

## Rails

| FPGA supply | Voltage | Power symbol | Pins on U4 |
|---|---|---|---|
| VCCINT | 1.0 V | `+1V0` | F7, F9, G6, H9, J6, K9, L8 (U4D) |
| VCCBRAM | 1.0 V | `+1V0` | E10, F11 (U4D) |
| VCCAUX | 1.8 V | `+1V8` | G10, J10, K11, L10 (U4D) |
| VCCO_0 | 3.3 V | `+3V3` | L6 (U4C, Section 4) |
| VCCO_14, VCCO_15 | 3.3 V | `+3V3` | U4A, Section 5 |
| VCCO_34 | 3.3 V | `+3V3` | M3, R4, T1 (U4B, Section 3) |
| VCCO_35 | **1.8 V** | `+1V8` | A6, B3, D7, E4, F1, J2 (U4B, Section 3) |

VCCINT and VCCBRAM share 1.0 V, and DS181 says to feed them from the same supply. VCCAUX and bank 35 share 1.8 V, which DS181 also allows.

## Connections, pin by pin (U4D)

- All 7 `VCCINT` pins and both `VCCBRAM` pins → `+1V0`
- All 4 `VCCAUX` pins → `+1V8`
- All 30 `GND` pins → `GND`
- `VCCADC_0` (G8) → `+1V8`, with C27 100nF to GND. The XADC isn't used, so no filter is needed.
- `GNDADC_0` (G7) → `GND`
- `VCCBATT_0` (F8) → `GND`. UG470: "connect this pin to GND or VCCAUX" when there's no encryption-key battery.

**Capacitors:** draw each one between its rail's power symbol and GND. Group them by rail in the box, labelled e.g. "VCCO_14 caps". The VCCO pins are in other sections, but the power symbols join everything.

## Layout notes (for later)

- The 1uF and 4.7uF capacitors go **on the bottom side, under the BGA**, between the vias of their rail. UG483 asks for them as close as possible to the pins they serve.
- The 47uF and 100uF capacitors can go anywhere nearby. UG483 says bulk capacitors aren't sensitive to location.
- Bottom-side parts cost a second JLC assembly side, so we'll check that price before layout. If it's too much, they go on top around the FPGA instead.

## Done-check

- [ ] U4 footprint set to `Package_BGA:Xilinx_FTG256`, LCSC C1521788
- [ ] U4D placed here. Units A, B and C are placed in their own sections (no unit left out)
- [ ] VCCINT ×7 + VCCBRAM ×2 → +1V0. VCCAUX ×4 + VCCADC → +1V8. GND ×30 + GNDADC + VCCBATT → GND
- [ ] 44 capacitors total in this section (C13–C56): 1 ×100uF, 7 ×47uF, 12 ×4.7uF, 23 ×1uF, 1 ×100nF (C27)
- [ ] `LCSC` field on every capacitor
