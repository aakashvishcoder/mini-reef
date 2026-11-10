# Section 3: HyperRAM (+ FPGA banks 34 and 35)

**What it does:** the 32 MB memory the whole project is about. It holds the TinyStories 28M weights, and its bandwidth is what you measure. The FPGA talks to it over HyperBus on **bank 35 at 1.8 V**. Bank 34 (3.3 V) also lives on this unit, and supplies the 8 debug pins.

Checked against the Winbond W958D8NBYA datasheet (rev A01-003) ball map and the KiCad FPGA symbol.

## Parts in this section

| Ref | Value | Symbol | Footprint | LCSC | JLC type |
|---|---|---|---|---|---|
| U4B | (FPGA unit B) | `FPGA_Xilinx_Artix7:XC7A15T-FTG256` | (set in Section 2) | — | — |
| U5 | W958D8NBYA5I | `mini-reef:W958D8NBYA` | `Package_BGA:BGA-24_6x8mm_Layout5x5_P1.0mm` | C7420405 | Extended |
| C57 | 1uF 0402 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C52923 | Basic |
| C58, C59, C60 | 100nF 0402 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C1525 | Basic |

`mini-reef:W958D8NBYA` is in the project symbol library (`mini-reef.kicad_sym`). It loads automatically when you open the project. I built it from the datasheet's ball map, and the footprint's 24 pads (A1 missing) match it.

## HyperRAM wiring

Draw these as **wires** or **local labels** inside this box. Both chips are here, so no global labels are needed.

| HyperRAM | Ball | Local label | FPGA ball (bank 35) | FPGA pin name |
|---|---|---|---|---|
| CK | B2 | `HR_CK` | E3 | IO_L11P_T1_SRCC_35 |
| CK# | B1 | `HR_CK_N` | D3 | IO_L11N_T1_SRCC_35 |
| CS# | A3 | `HR_CS_N` | C4 | IO_L12N_T1_MRCC_35 |
| RWDS | C3 | `HR_RWDS` | D4 | IO_L12P_T1_MRCC_35 |
| DQ0 | D3 | `HR_DQ0` | C3 | IO_L7P_T1_AD6P_35 |
| DQ1 | D2 | `HR_DQ1` | C2 | IO_L7N_T1_AD6N_35 |
| DQ2 | C4 | `HR_DQ2` | B2 | IO_L8P_T1_AD14P_35 |
| DQ3 | D4 | `HR_DQ3` | A2 | IO_L8N_T1_AD14N_35 |
| DQ4 | D5 | `HR_DQ4` | C1 | IO_L9P_T1_DQS_AD7P_35 |
| DQ5 | E3 | `HR_DQ5` | B1 | IO_L9N_T1_DQS_AD7N_35 |
| DQ6 | E2 | `HR_DQ6` | E2 | IO_L10P_T1_AD15P_35 |
| DQ7 | E1 | `HR_DQ7` | D1 | IO_L10N_T1_AD15N_35 |
| RESET# | A4 | `HR_RST_N` | G5 | IO_L16P_T2_35 |

**Why these pins:**
- **Byte group T1:** DQ0–7, RWDS, CK and CS# all sit in bank 35's byte group T1 (pairs L7–L12). That keeps them under one clock region, which the PRD requires for IDELAY/ISERDES capture.
- **RWDS on a clock-capable pin:** it's on L12P (MRCC) so it can act as the read strobe.
- **CK/CK# on a true pair:** L11P/L11N, so they can be a differential output.
- **Corner of the BGA:** these balls are at the FPGA's top-left corner, so the HyperRAM sits just left of the FPGA. That suits a 4-layer board.
- **Still to confirm:** PRD milestone 2 is to confirm this pinout in Vivado's I/O planner before layout.

## Power and unused pins

- **U5 power:**
  - `VCC` (B4), `VCCQ` (D1) and `VCCQ` (E4) → `+1V8`. Each gets one 100nF: C58, C59, C60. Add C57 1uF near the chip.
  - `VSS` (B3), `VSSQ` (C1) and `VSSQ` (E5) → `GND`
  - The 5 `RFU` pins are already marked no-connect in the symbol, so leave them.
- **U4B power:**
  - All 6 `VCCO_35` → `+1V8`
  - All 3 `VCCO_34` → `+3V3`
- **RESET#** has a weak internal pull-up, and PUDC_B (Section 5) turns on the FPGA's pull-ups during configuration. That keeps CS# and RESET# high, so the RAM stays idle until your design starts.

## Debug pins (bank 34, 3.3 V)

These are the PRD's 8 measurement pins (R9). Put global labels on these U4B balls. All are on the outer rows, so they're easy to route.

| Global label | Shape | Direction | FPGA ball |
|---|---|---|---|
| `DBG0` | Output | Points **down** to Section 6 | M1 (IO_L2N_T0_34) |
| `DBG1` | Output | down | N1 (IO_L4P_T0_34) |
| `DBG2` | Output | down | P1 (IO_L4N_T0_34) |
| `DBG3` | Output | down | R1 (IO_L7N_T1_34) |
| `DBG4` | Output | down | R2 (IO_L7P_T1_34) |
| `DBG5` | Output | down | T2 (IO_L8N_T1_34) |
| `DBG6` | Output | down | T3 (IO_L9N_T1_DQS_34) |
| `DBG7` | Output | down | T4 (IO_L9P_T1_DQS_34) |

## Unused FPGA pins

Leave every other I/O on U4B unconnected. Don't hand-place ~60 no-connect flags. When the whole schematic is drawn, I'll add them to unused I/O with a script, then show you the change before it's saved.

## Power budget update

HyperRAM: 12–22 mA at 1.8 V when active (datasheet ICC1/ICC2), up to 35 mA during power-up. That's well inside the +1V8 rail's estimate in Section 1.

## Done-check

- [ ] U5 is `mini-reef:W958D8NBYA`, footprint `BGA-24_6x8mm_Layout5x5_P1.0mm`, LCSC C7420405
- [ ] All 13 HyperBus signals on the balls in the table (double-check DQ order: it isn't sequential on either chip)
- [ ] U5 VCC/VCCQ → +1V8 with C57–C60. VSS/VSSQ → GND
- [ ] VCCO_35 ×6 → +1V8. VCCO_34 ×3 → +3V3
- [ ] DBG0–DBG7 global labels on M1, N1, P1, R1, R2, T2, T3, T4
