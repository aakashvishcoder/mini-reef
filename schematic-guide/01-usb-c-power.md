# Section 1: USB-C & Power

**What it does:** takes 5 V from the USB-C cable and makes the board's three rails: **1.0 V** (FPGA core), **1.8 V** (FPGA auxiliary, HyperRAM) and **3.3 V** (FPGA I/O, flash, CH347T). They turn on one after another in the order AMD recommends: 1.0, then 1.8, then 3.3.

Checked 2026-11-09 against the TI TPS6213x datasheet (SLVSAG7F), AMD DS181 v1.27.1, and JLC's part pages.

## Parts in this section

| Ref | Value | Symbol | Footprint | LCSC |
|---|---|---|---|---|
| J1 | USB-C receptacle | `Connector:USB_C_Receptacle_USB2.0_16P` | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 |
| F1 | 1.1A PTC fuse | `Device:Polyfuse` | `Fuse:Fuse_1206_3216Metric` | C20801 |
| U1, U2, U3 | TPS62130A | `Regulator_Switching:TPS62130A` | `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias` | C337502 |
| L1, L2, L3 | 2.2uH | `Device:L` | `mini-reef:IND-SMD_L4.5-W4.1_SRP4020TA` | C719179 |
| C1, C4, C5, C8, C9, C12 | 22uF | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | C45783 |
| C2, C6, C10 | 100nF | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C1525 |
| C3, C7, C11 | 10nF | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C15195 |
| R1, R2, R3 | 5.1k | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25905 |
| R4 | 20k | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25765 |
| R5, R6 | 100k | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25741 |
| R7, R10 | 15k | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25756 |
| R8 | 12k | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25752 |
| R9 | 47k | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25792 |
| R11 | 1k | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C11702 |
| D1 | Red LED | `Device:LED` | `LED_SMD:LED_0603_1608Metric` | C2286 |
| TP1–TP7 | Test points | `Connector:TestPoint` | `TestPoint:TestPoint_Pad_D1.5mm` | none (tick **Exclude from BOM**) |

**Power symbols** (from the `power` library, not counted as parts): `VBUS`, `+5V`, `+1V0`, `+1V8`, `+3V3`, `GND`, `PWR_FLAG`.

Put each LCSC number in a field named `LCSC`, same as the last board. JLC type: **Extended** for J1, F1, U1–U3 and L1–L3 (4 types, ~$12 in fees). Everything else is **Basic** (no fee). All part numbers were confirmed on JLC's pages. Live stock gets re-checked at the final quote.

## Before you draw (once)

1. KiCad → **File → New Project** → `~/Documents/mini-reef` → name `mini-reef` → **untick "Create a new folder"**.
2. Schematic → **File → Page Settings → A2**.
3. Draw 6 labelled boxes: top row `1 USB-C & Power`, `2 FPGA Power`, `3 HyperRAM`; bottom row `4 USB-JTAG & Console`, `5 Clock & Config`, `6 Test Host & Debug`. Section 1 goes in the top-left box.

## Global labels in this section

| Label | Shape | Direction | Connects to | Other end |
|---|---|---|---|---|
| `USB_DP` | Bidirectional | Points **down** to box 4 | J1 A6 + B6 | CH347T pin 17 (Section 4) |
| `USB_DN` | Bidirectional | Points **down** | J1 A7 + B7 | CH347T pin 16 |

**Local labels** (**Place → Net Label**, used only inside this box): `PG_1V0` and `PG_1V8`.

## Circuit

```
J1 VBUS ──●── F1 1.1A ──●── +5V
          TP1            TP2
CC1 ── R1 5.1k ── GND        CC2 ── R2 5.1k ── GND        GND, SHIELD ── GND

Each regulator (U1 shown; values for U2 and U3 in the table below):

  +5V ──●── VIN 10,11,12 ─┐      ┌─ SW 1,2,3 ── L1 2.2uH ──●── +1V0 ── TP3
     C1 22uF, C2 100nF    │  U1  │                          │
        to GND            │      ├─ VOS 14 ─────────────────●
  +5V ────── EN 13 ───────┤      │                   C4 22uF to GND
           SS/TR 9 ─ C3 ─ GND    ├─ FB 5 ──●── R3 5.1k ── +1V0
           FSW 7 ─── GND         │         └── R4 20k ─── GND
           DEF 8 ─── GND         ├─ PG 4 ── PG_1V0 ── R5 100k ── +5V
                                 └─ GND 6,15,16,17 ── GND

+3V3 ── R11 1k ── D1 ►|── GND
```

| | U1 → +1V0 | U2 → +1V8 | U3 → +3V3 |
|---|---|---|---|
| EN (pin 13) | **+5V** | `PG_1V0` | `PG_1V8` |
| Input caps (22uF / 100nF) | C1 / C2 | C5 / C6 | C9 / C10 |
| Soft-start (10nF) | C3 | C7 | C11 |
| Inductor | L1 | L2 | L3 |
| Output cap (22uF) | C4 | C8 | C12 |
| FB top (to output) | R3 5.1k | R7 15k | R9 47k |
| FB bottom (to GND) | R4 20k | R8 12k | R10 15k |
| PG (pin 4) | `PG_1V0` + R5 100k → +5V | `PG_1V8` + R6 100k → +5V | **no-connect flag** |
| Output test point | TP3 | TP4 | TP5 |

## Connections, pin by pin

**J1 (USB-C)**
- `VBUS` pins (A4, A9, B4, B9) → `VBUS` symbol, plus TP1
- `CC1` (A5) → R1 5.1k → GND. `CC2` (B5) → R2 5.1k → GND. **Each CC pin needs its own resistor.**
- `D+` (A6, B6) → `USB_DP`. `D−` (A7, B7) → `USB_DN`
- `GND` (A1, A12, B1, B12) and `SHIELD` → GND
- `SBU1` (A8), `SBU2` (B8) → no-connect flags

**F1:** pin 1 → `VBUS`, pin 2 → `+5V`. TP2 on `+5V`.

**U1, U2, U3 (TPS62130A).** Every regulator is wired the same way. Only the rows in the table above differ.
- Pins 10, 11, 12 `VIN` → `+5V`. Input 22uF and 100nF from `+5V` to GND, right next to the chip.
- Pins 1, 2, 3 `SW` → inductor pin 1. Inductor pin 2 → the output rail.
- Pin 14 `VOS` → the output rail, on the inductor's output side.
- Pin 5 `FB` → middle of the two divider resistors. Top resistor to the output rail, bottom resistor to GND.
- Pin 9 `SS/TR` → 10nF → GND
- Pin 7 `FSW` → GND (2.5 MHz). Pin 8 `DEF` → GND (nominal voltage).
- Pin 13 `EN` → from the table
- Pin 4 `PG` → from the table. U3's PG is unused: put a no-connect flag on it. The datasheet allows PG to float, and tying it to GND makes ERC report an open-collector-vs-power error.
- Pins 6, 15, 16, 17 `GND` (17 is the center pad) → GND
- Output 22uF from the rail to GND. Test point on the rail.

**D1 / R11:** `+3V3` → R11 1k → D1 anode. D1 cathode → GND (triangle points to GND). D1 lit means all three rails are up, because 3.3 V comes last.

**TP6, TP7** → GND.

**PWR_FLAG:** one each on `VBUS`, `+5V`, `+1V0`, `+1V8`, `+3V3` and `GND`. The rails come out through inductors, so ERC can't tell they're driven.

## Why it's built this way

1. **It must be the TPS62130A, not the TPS62130.** The A version holds PG low while it's off (datasheet Table 8-2). On the plain TPS62130, PG floats and would turn the next rail on too early.
2. **Turn-on order 1.0, then 1.8, then 3.3 V** is DS181's recommended order (VCCINT, VCCBRAM, VCCAUX, VCCO). Each regulator's PG enables the next.
3. **10nF soft-start gives a 5 ms ramp** (C × 1.25 V / 2.5 µA). DS181 allows 0.2–50 ms. The datasheet's 3.3nF is an Extended part, so 10nF saves $3.
4. **Output voltages** from Vout = 0.8 V × (1 + top/bottom):

| Rail | Divider | Vout | Allowed |
|---|---|---|---|
| +1V0 | 5.1k / 20k | 1.004 V | 0.95–1.05 V |
| +1V8 | 15k / 12k | 1.800 V | 1.71–1.89 V |
| +3V3 | 47k / 15k | 3.307 V | up to 3.465 V |

5. **Buck converters, not LDOs.** They draw about 0.4 A from USB instead of about 0.6 A, and they have the enable pins the sequencing needs.
6. **No USB ESD chip.** The PRD keeps anything that doesn't serve a measurement off v1. It saves about $4, at the cost of less protection on the USB port.
7. **1.1 A fuse.** The board draws about 0.4 A, which would sit too close to a 500 mA fuse's rating.

## Power budget (estimate)

| Rail | Startup minimum (DS181) | Running estimate | From 5 V |
|---|---|---|---|
| +1V0 | 215 mA VCCINT + 62 mA VCCBRAM | ~600 mA | ~0.14 A |
| +1V8 | 62 mA VCCAUX + 41 mA VCCO + up to 35 mA HyperRAM | ~250 mA | ~0.11 A |
| +3V3 | 41 mA per bank | ~200 mA | ~0.15 A |
| **Total** | | **~1.7 W** | **~0.4 A** |

The running figures are my estimate. PRD R5 needs AMD's Power Estimator once your RTL exists. Each regulator handles 3 A.

## Bring-up test (after boards arrive)

1. **Unplugged:** TP2–TP5 to TP6 must not read a short.
2. **Plug into a USB charger through a USB power meter.** Expect under about 0.5 A, and D1 lit.
3. **Read each test point:**

| Point | Rail | Expected |
|---|---|---|
| TP1 | VBUS | 4.75–5.25 V |
| TP2 | +5V | Same as TP1, minus a little |
| TP3 | +1V0 | 0.95–1.05 V |
| TP4 | +1V8 | 1.71–1.89 V |
| TP5 | +3V3 | 3.14–3.46 V |

4. **If a rail is missing,** the one before it isn't raising PG. Check rails in order from TP3.

## Done-check

- [ ] U1–U3 are **TPS62130A** (C337502)
- [ ] U1 EN → +5V, U2 EN → `PG_1V0`, U3 EN → `PG_1V8`. U3 PG → no-connect flag
- [ ] U2 and U3 VIN → `+5V` (not the PG label: EN and VIN are separate wires on U2 and U3)
- [ ] Divider values match the table, top resistor to the output rail, bottom to GND
- [ ] VOS on the output side of each inductor
- [ ] FSW and DEF → GND on all three
- [ ] CC1 and CC2 each have their own 5.1k
- [ ] `PWR_FLAG` on all six power nets
- [ ] `LCSC` field and footprint on every part. TP1–TP7 set to Exclude from BOM

Save and tell me. I'll run ERC and check every pin. `USB_DP` and `USB_DN` will warn about having only one end until Section 4 is drawn; that's expected.
