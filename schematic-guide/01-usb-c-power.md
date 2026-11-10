# Section 1: USB-C & Power

**What it does:** takes 5 V from a USB-C cable and makes the three rails the board needs: **1.0 V** (FPGA core), **1.8 V** (FPGA auxiliary, HyperRAM) and **3.3 V** (FPGA I/O, flash, USB-JTAG chip). The rails turn on one after another, in the order AMD recommends.

Checked 2026-11-09 against the TPS6213x datasheet (SLVSAG7F) and AMD DS181 v1.27.1.

## Project setup (do this once)

1. KiCad → **File → New Project**. Save it as `mini-reef` inside `~/Documents/mini-reef`. **Untick "Create a new folder"**: the folder already exists and holds a footprint library you need.
2. In the schematic: **File → Page Settings → A2**. The FPGA symbol is large.
3. Draw 6 labelled boxes on the one sheet, like the RISC-V board: `1 USB-C & Power`, `2 FPGA Power & Banks`, `3 HyperRAM`, `4 USB-JTAG & Console`, `5 Clock & Config`, `6 Test Host & Debug`.

## Parts in this section

| Ref | Value | Symbol | Footprint | LCSC | JLC type |
|---|---|---|---|---|---|
| J1 | USB-C receptacle | `Connector:USB_C_Receptacle_USB2.0_16P` | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | Extended |
| F1 | 1.1 A hold PTC, 6 V | `Device:Polyfuse` | `Fuse:Fuse_1206_3216Metric` | C20801 | Extended |
| R1, R2 | 5.1k (CC pull-downs) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25905 | Basic |
| U1, U2, U3 | TPS62130A | `Regulator_Switching:TPS62130A` | `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias` | C337502 | Extended |
| L1, L2, L3 | 2.2uH SRP4020TA | `Device:L` | `mini-reef:IND-SMD_L4.5-W4.1_SRP4020TA` | C719179 | Extended |
| C1, C4, C5, C8, C9, C12 | 22uF 25V 0805 | `Device:C` | `Capacitor_SMD:C_0805_2012Metric` | C45783 | Basic |
| C2, C6, C10 | 100nF 0402 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C1525 | Basic |
| C3, C7, C11 | 10nF 0402 (soft-start) | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C15195 | Basic |
| R3 | 5.1k (1.0 V top) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25905 | Basic |
| R4 | 20k (1.0 V bottom) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25765 | Basic |
| R5, R6 | 100k (PG pull-ups) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25741 | Basic |
| R7 | 15k (1.8 V top) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25756 | Basic |
| R8 | 12k (1.8 V bottom) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25752 | Basic |
| R9 | 47k (3.3 V top) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25792 | Basic |
| R10 | 15k (3.3 V bottom) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25756 | Basic |
| R11 | 1k (LED) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C11702 | Basic |
| D1 | Red LED 0603 | `Device:LED` | `LED_SMD:LED_0603_1608Metric` | C2286 | Basic |
| TP1–TP7 | Test points | `Connector:TestPoint` | `TestPoint:TestPoint_Pad_D1.5mm` | none | Exclude from BOM |

Put each LCSC number in a field named `LCSC`, same as the last board.

**Cost:** 4 extended part types here (about $12 in JLC fees). Using one regulator and one inductor for all three rails means one fee each, not three. Every resistor and small capacitor is a JLC Basic part with no fee.

**Stock caveat:** JLC's pages confirmed the Basic/Extended types above, but neither JLC nor LCSC would show me live stock. TPS62130A, the inductor and J1 all went through JLC's system on your earlier orders. We re-check every part at the final quote.

## Key decisions (from the datasheets)

1. **TPS62130A, not TPS62130.** Its PG pin stays **low** while the chip is off (datasheet Table 8-2). On the plain TPS62130 PG goes high-impedance, so its pull-up would turn the next rail on too early.
2. **Turn-on order 1.0 V → 1.8 V → 3.3 V.** DS181 recommends VCCINT, VCCBRAM, VCCAUX, then VCCO, for minimum current and so the I/Os stay tri-stated. PG of each regulator drives EN of the next. VCCINT and VCCBRAM share 1.0 V, as DS181 says to.
3. **Soft-start 10nF = 5 ms.** tSS = C × 1.25 V / 2.5 µA. DS181 allows 0.2–50 ms per rail. The datasheet example uses 3.3nF, but that value is an Extended part, so 10nF saves $3.
4. **Buck converters, not AMS1117s.** Cheap LDOs would pull about 0.6 A from USB and have no enable pin to sequence with. Bucks draw about 0.4 A.
5. **No USB ESD chip.** The PRD keeps anything that doesn't serve a measurement off v1. It saves about $4. The tradeoff is less protection on the USB port.
6. **1.1 A fuse, not the 500 mA one** from the RISC-V board. This board's estimated 0.4 A would sit too close to a 500 mA hold rating.

**Output voltages** (Vout = 0.8 V × (1 + Rtop / Rbottom)):

| Rail | Rtop / Rbottom | Vout | Allowed |
|---|---|---|---|
| +1V0 | 5.1k / 20k | 1.004 V | 0.95–1.05 V |
| +1V8 | 15k / 12k | 1.800 V | 1.71–1.89 V |
| +3V3 | 47k / 15k | 3.307 V | up to 3.465 V |

## Labels in this section

Use **power symbols** for `VBUS`, `+5V`, `+1V0`, `+1V8`, `+3V3` and `GND` (not labels). They connect across the whole sheet.

| Global label | Shape | Direction | Connects to | Other end |
|---|---|---|---|---|
| `USB_DP` | Bidirectional | Points **right** | J1 A6 + B6 | Section 4, CH347T |
| `USB_DN` | Bidirectional | Points **right** | J1 A7 + B7 | Section 4, CH347T |

Two **local** labels (`Place → Net Label`), used only in this box: `PG_1V0` and `PG_1V8`.

## Circuit

```
J1 VBUS ──●── F1 1.1A ──●── +5V
          TP1            TP2

CC1 ── R1 5.1k ── GND       CC2 ── R2 5.1k ── GND       SHIELD, GND ── GND

        +5V                    PG_1V0                  PG_1V8
         │                       │                       │
U1 EN ───┘             U2 EN ────┘             U3 EN ────┘

Each regulator (U1 shown; values for U2, U3 in the table below):

  +5V ──●── VIN 10,11,12 ─┐      ┌─ SW 1,2,3 ── L1 2.2uH ──●── +1V0
     C1 22uF, C2 100nF    │  U1  │                          │
        to GND            │      ├─ VOS 14 ─────────────────●
                 SS/TR 9 ─┤      │                 C4 22uF to GND
              C3 10nF to GND     ├─ FB 5 ──●── R3 ── +1V0
                 FSW 7 ── GND    │         └── R4 ── GND
                 DEF 8 ── GND    ├─ PG 4 ── PG_1V0 ── R5 100k ── +5V
                                 └─ GND 6,15,16,17 ── GND
```

| Part | U1 → +1V0 | U2 → +1V8 | U3 → +3V3 |
|---|---|---|---|
| EN (pin 13) | **+5V** | `PG_1V0` | `PG_1V8` |
| PVIN caps (22uF / 100nF) | C1 / C2 | C5 / C6 | C9 / C10 |
| Soft-start (10nF) | C3 | C7 | C11 |
| Inductor | L1 | L2 | L3 |
| Output cap (22uF) | C4 | C8 | C12 |
| FB top, to output | R3 5.1k | R7 15k | R9 47k |
| FB bottom, to GND | R4 20k | R8 12k | R10 15k |
| PG (pin 4) | `PG_1V0` + R5 100k to +5V | `PG_1V8` + R6 100k to +5V | **GND** (unused) |
| Output test point | TP3 | TP4 | TP5 |

**The rest:**
- `+3V3` → R11 1k → D1 → GND (triangle points to GND). D1 lit means all three rails came up, since 3.3 V is last.
- TP6, TP7 → GND.

## Connections, pin by pin

**J1**
- All `VBUS` pins → `VBUS` symbol, plus TP1.
- `CC1` → R1 → GND. `CC2` → R2 → GND. They tell a USB-C port to supply 5 V.
- `A6`, `B6` (D+) → `USB_DP`. `A7`, `B7` (D−) → `USB_DN`.
- `GND` and `SHIELD` → GND. `SBU1`, `SBU2` → no-connect flags.

**F1** between `VBUS` and `+5V`. TP2 on `+5V`.

**ERC flags:** add one `PWR_FLAG` each on `VBUS`, `+5V`, `+1V0`, `+1V8`, `+3V3` and `GND`. The rails come out through inductors, so ERC can't tell they're driven.

## Power budget (estimate)

| Rail | Startup minimum (DS181) | Running estimate | From 5 V |
|---|---|---|---|
| +1V0 | 215 mA VCCINT + 62 mA VCCBRAM | ~600 mA | ~0.14 A |
| +1V8 | 62 mA VCCAUX + 41 mA VCCO bank | ~250 mA | ~0.11 A |
| +3V3 | 41 mA per bank | ~200 mA | ~0.15 A |
| **Total** | | **~1.7 W** | **~0.4 A at 85% efficiency** |

Startup figures are from DS181 Table 6. The running figures are my estimate, since they depend on your RTL. PRD R5 needs a real check: run AMD's Power Estimator once the design exists, and I'll add HyperRAM current in Section 3. Each regulator is good for 3 A, so there's plenty of margin.

## Bring-up test (after boards arrive)

1. **Unplugged:** measure TP2–TP5 to TP6. None should read a short.
2. **Plug into a USB charger through a USB power meter.** Expect under about 0.5 A, and D1 lit.
3. **Read each test point:**

| Point | Rail | Expected |
|---|---|---|
| TP1 | VBUS | 4.75–5.25 V |
| TP2 | +5V | Same as TP1, minus a little |
| TP3 | +1V0 | 0.95–1.05 V |
| TP4 | +1V8 | 1.71–1.89 V |
| TP5 | +3V3 | 3.14–3.46 V |

4. **If a later rail is missing,** the one before it isn't reaching PG. Check rails in order from TP3.

## Done-check

- [ ] 3 regulators are **TPS62130A** (C337502)
- [ ] U1 EN → +5V, U2 EN → `PG_1V0`, U3 EN → `PG_1V8`
- [ ] Divider values match the table, top resistor to the output, bottom to GND
- [ ] VOS (pin 14) on the output side of each inductor
- [ ] FSW and DEF → GND on all three. U3 PG → GND
- [ ] CC1 and CC2 each have their own 5.1k. A6+B6 = `USB_DP`, A7+B7 = `USB_DN`
- [ ] `LCSC` field and footprint on every part
- [ ] `PWR_FLAG` on all six power nets

Save and tell me. I'll run ERC and check every pin. Expected: `USB_DP` and `USB_DN` will warn about being connected at only one end until Section 4 is drawn.
