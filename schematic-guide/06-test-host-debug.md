# Section 6: Test Host, Debug Header, LEDs & Button

**What it does:** the parts you touch and probe.
- **J3:** connects to your CH32V307 board, which loads test vectors, starts runs and reads pass/fail (PRD R8).
- **J4:** 8 debug pins for a logic analyzer or scope (PRD R9).
- **2 LEDs and a button** for your RTL (PRD R10).

This is the last section. After it, every global label has both ends.

## Parts in this section

| Ref | Value | Symbol | Footprint | LCSC | JLC type |
|---|---|---|---|---|---|
| J3 | Test-host header 2x6 | `Connector_Generic:Conn_02x06_Odd_Even` | `Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical` | (you solder) | Exclude from BOM |
| J4 | Debug header 2x6 | `Connector_Generic:Conn_02x06_Odd_Even` | `Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical` | (you solder) | Exclude from BOM |
| D2, D3 | Red LED 0603 | `Device:LED` | `LED_SMD:LED_0603_1608Metric` | C2286 | Basic |
| R19, R20 | 1k 0402 | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C11702 | Basic |
| SW1 | Button | `Switch:SW_Push` | `Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A` | C318884 | Basic |
| R21 | 4.7k (button pull-up) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25900 | Basic |

The LEDs, resistors and button are the same parts as on your RISC-V board. **J2, J3, J4 and JP1** all come from one 2.54 mm 2×40 male header strip, which you snap apart and solder (about $1).

## Labels in this section

All of these already exist, so pick them from the dropdown. Shapes are from **this section's** side. Point every label **left**, toward Section 5 (and up-left toward Section 3 for `DBG`).

| Label | Shape | Connects to |
|---|---|---|
| `HOST_SCK`, `HOST_MOSI`, `HOST_CS_N`, `HOST_RST_N`, `HOST_START` | Output | J3 (driven by the CH32V307) |
| `HOST_MISO`, `HOST_DONE`, `HOST_PASS` | Input | J3 (driven by the FPGA) |
| `DBG0` … `DBG7` | Input | J4 |
| `LED0`, `LED1` | Input | R19 → D2, R20 → D3 |
| `BTN_N` | Output | SW1 + R21 |

## Connections, pin by pin

**J3 test-host header.** Every signal sits next to a ground (PRD: at least one ground per two signals).

| J3 pin | Net | CH32V307 board, J5 pin |
|---|---|---|
| 1 | `HOST_SCK` | 7 (PB13, SPI2 SCK) |
| 2 | GND | 10 (GND) |
| 3 | `HOST_MOSI` | 9 (PB15, SPI2 MOSI) |
| 4 | `HOST_MISO` | 8 (PB14, SPI2 MISO) |
| 5 | GND | GND |
| 6 | `HOST_CS_N` | 6 (PB12, SPI2 NSS) |
| 7 | `HOST_RST_N` | 4 (PB10) |
| 8 | GND | GND |
| 9 | `HOST_START` | 5 (PB11) |
| 10 | `HOST_DONE` | 2 (PB6) |
| 11 | GND | GND |
| 12 | `HOST_PASS` | 3 (PB7) |

**No power pin on J3.** Each board runs from its own USB cable, and only grounds are shared. That way neither board can back-power the other. Your RISC-V board's J5 has just one GND, so use its J4 pin 10 and J3 pin 4 as extra grounds for the jumper wires.

**J4 debug header,** same pattern: 1 `DBG0`, 2 GND, 3 `DBG1`, 4 `DBG2`, 5 GND, 6 `DBG3`, 7 `DBG4`, 8 GND, 9 `DBG5`, 10 `DBG6`, 11 GND, 12 `DBG7`.

**LEDs (active-high: drive 1 = on)**
- `LED0` → R19 1k → D2 anode. D2 cathode → GND.
- `LED1` → R20 1k → D3 anode. D3 cathode → GND.

**Button**
- `BTN_N` → SW1 → GND, plus R21 4.7k → `+3V3`. Pressed reads 0. Use it as your RTL's reset or start.

## Bring-up test (after boards arrive)

1. A bitstream that echoes `BTN_N` to `LED0`: pressing SW1 lights D2.
2. **Test-host link (PRD step 7):** the CH32V307 sends a few bytes over SPI2, pulses `HOST_START`, and waits for `HOST_DONE`. It then reads `HOST_PASS`.
3. **Debug pins:** toggle `DBG0–7` from a counter and check each pin with a scope or logic analyzer.

## Done-check

- [ ] J3 pinout matches the table, with grounds on 2, 5, 8 and 11
- [ ] J4: DBG0–7 with the same ground pattern
- [ ] LED triangles point toward GND
- [ ] SW1 to GND with R21 to +3V3
- [ ] J3 and J4 marked **Exclude from BOM**
- [ ] `LCSC` field on D2, D3, R19–R21 and SW1

Save and tell me. Then I'll:
1. Add no-connect flags to every unused FPGA pin, and show you the change before saving.
2. Run full-board ERC (expected: 0 errors).
3. Export the netlist so the pinout can go into Vivado's I/O planner (PRD milestone 2).
