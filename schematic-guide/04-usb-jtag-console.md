# Section 4: USB-JTAG & Console (+ FPGA bank 0)

**What it does:** one CH347T chip gives your computer two things over the USB-C cable: a **JTAG port** to load bitstreams and flash, and a **serial console** to the FPGA. FPGA bank 0 (JTAG pins and configuration straps) lives here too.

Checked against the WCH CH347 datasheet v1.4 (TSSOP-20 pin table and mode table) and AMD UG470 v1.17.

## Parts in this section

| Ref | Value | Symbol | Footprint | LCSC | JLC type |
|---|---|---|---|---|---|
| U4C | (FPGA unit C) | `FPGA_Xilinx_Artix7:XC7A15T-FTG256` | (set in Section 2) | — | — |
| U6 | CH347T | `mini-reef:CH347T` | `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm` | C5122332 | Extended |
| Y1 | 8MHz crystal | `Device:Crystal` | `Crystal:Crystal_SMD_5032-2Pin_5.0x3.2mm` | C115962 | Basic |
| C61 | 100nF 0402 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C1525 | Basic |
| C62, C63 | 20pF 0402 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C1554 | Basic |
| R12, R13 | 4.7k (mode pull-downs) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25900 | Basic |
| R14, R15 | 4.7k (PROGRAM_B, INIT_B) | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25900 | Basic |
| J2 | JTAG header 1x6 | `Connector_Generic:Conn_01x06` | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` | (you solder) | Exclude from BOM |
| JP1 | CH347 off jumper 1x2 | `Connector_Generic:Conn_01x02` | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | (you solder) | Exclude from BOM |

The crystal and 20pF caps are the same parts as on your RISC-V board.

## Key decisions (from the datasheets)

1. **Mode 3 = one serial port + JTAG.** The CH347T reads DTR1 (pin 10) and RTS1 (pin 13) at reset. Both pulled low selects mode 3, and R12/R13 do that. Its USB product ID is then 0x55DD, which `openFPGALoader` uses with `--cable ch347_jtag`.
2. **8 MHz crystal with about 22pF loads** (datasheet §5.1). The 20pF parts are close enough.
3. **No series resistors on UD+/UD−.** The datasheet says the USB pins must connect straight to the bus.
4. **JP1 is the fallback.** If the CH347 won't drive the FPGA, put a jumper on JP1. That holds the CH347 in reset, and its pins stop driving. Then a normal JTAG cable on J2 takes over. J2 is also the PRD's required JTAG header.
5. **Configuration straps (UG470):**
   - M[2:0] = 001 boots from SPI flash
   - CFGBVS high, because bank 0 and bank 14 are 3.3 V
   - PROGRAM_B and INIT_B each need a pull-up of 4.7k or less
   - DONE has its own internal ~10k pull-up, so it's left open

## Labels in this section

| Global label | Shape | Direction | Connects to | Other end |
|---|---|---|---|---|
| `USB_DP` | Bidirectional | Points **up** to Section 1 | U6 pin 17 (UD+) | J1 in Section 1 |
| `USB_DN` | Bidirectional | Points **up** | U6 pin 16 (UD−) | J1 |
| `UART_TX` | **Input** | Points **right** to Section 5 | U6 pin 4 (RXD1) | FPGA T9 |
| `UART_RX` | **Output** | Points **right** | U6 pin 3 (TXD1) | FPGA T10 |
| `FLASH_CLK` | Output | Points **right** | U4C E8 (CCLK_0) | Flash in Section 5 |

`UART_TX`/`UART_RX` are named from the **FPGA's** side. The CH347 receives what the FPGA transmits, so its shape here is Input.

## Connections, pin by pin

**U6 CH347T**
- Pin 14 `VCC` → `+3V3`, with C61 100nF right at the pin. Pin 18 `GND` → GND.
- Pin 19 `XI` and pin 20 `XO` → Y1. Each side of Y1 → its own 20pF (C62, C63) → GND.
- Pin 17 `UD+` → `USB_DP`. Pin 16 `UD−` → `USB_DN`.
- Pin 10 `DTR1/MODE0` → R12 4.7k → GND. Pin 13 `RTS1/MODE1` → R13 4.7k → GND.
- Pin 1 `RST#` → JP1 pin 1. JP1 pin 2 → GND. It has an internal pull-up, so it runs when the jumper is off.
- Pin 3 `TXD1` → `UART_RX`. Pin 4 `RXD1` → `UART_TX`.
- JTAG to U4C, drawn as wires:

| U6 pin | U4C pin |
|---|---|
| 5 `TMS` | M7 `TMS_0` |
| 6 `TCK` | L7 `TCK_0` |
| 8 `TDI` | N7 `TDI_0` (CH347 sends, FPGA receives) |
| 7 `TDO` | N8 `TDO_0` (FPGA sends, CH347 receives) |

- Pins 2 `CTS1`, 9 `TRST`, 11 and 12 `GPIO`, and 15 `ACT#` → no-connect flags.

**J2 JTAG header** (same order as Digilent's 6-pin JTAG cables):
| J2 pin | Net |
|---|---|
| 1 | `+3V3` (VREF) |
| 2 | TMS |
| 3 | TCK |
| 4 | TDO |
| 5 | TDI |
| 6 | GND |

Each JTAG line joins the same net as the U6 ↔ U4C wire above.

**U4C (bank 0)**
- `VCCO_0` (L6) → `+3V3`. Its 47uF (C28) is in Section 2.
- `CFGBVS_0` (E7) → `+3V3`
- `M0_0` (M9) → `+3V3`. `M1_0` (M10) → GND. `M2_0` (M11) → GND. That's 001, Master SPI.
- `PROGRAM_B_0` (L9) → R14 4.7k → `+3V3`
- `INIT_B_0` (K10) → R15 4.7k → `+3V3`
- `DONE_0` (H10) → no-connect flag (internal pull-up)
- `CCLK_0` (E8) → `FLASH_CLK`
- XADC not used:
  - `VP_0` (H8), `VN_0` (J7), `VREFP_0` (J8) and `VREFN_0` (H7) → GND. VREFP/N to ground selects the internal reference.
  - `DXP_0` (K8) and `DXN_0` (K7) → GND (temperature diode not used).

## Bring-up test (after boards arrive)

1. Plug in USB-C. The computer shows one serial port and one CH347 JTAG device (USB ID 1a86:55dd).
2. Run `openFPGALoader --cable ch347_jtag --detect`. It should report an XC7A15T (or XC7A35T) IDCODE. This is PRD bring-up step 2.
3. Load a blink bitstream: `openFPGALoader --cable ch347_jtag blink.bit`
4. If step 2 fails: put a jumper on JP1, connect a JTAG cable to J2, and repeat with that cable.

## Done-check

- [ ] R12 and R13 pull pins 10 and 13 **low** (mode 3)
- [ ] TDI goes CH347 pin 8 → FPGA N7, and TDO goes FPGA N8 → CH347 pin 7 (not swapped)
- [ ] Y1 with a 20pF on each side. C61 on VCC
- [ ] M0 high, M1 and M2 low. CFGBVS high
- [ ] 4.7k pull-ups on PROGRAM_B and INIT_B
- [ ] J2 and JP1 marked **Exclude from BOM** (you solder them)
