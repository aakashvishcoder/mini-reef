# Section 5: Clock & Config Flash (+ FPGA banks 14 and 15)

**What it does:** gives the FPGA its 50 MHz clock and the SPI flash it boots from. It also holds FPGA unit A (banks 14 and 15, 3.3 V), which carries the console, test-host link, LEDs and button.

Checked against AMD UG470 v1.17 (Master SPI x4, Figure 2-14) and the KiCad symbols.

## Parts in this section

| Ref | Value | Symbol | Footprint | LCSC | JLC type |
|---|---|---|---|---|---|
| U4A | (FPGA unit A) | `FPGA_Xilinx_Artix7:XC7A15T-FTG256` | (set in Section 2) | — | — |
| U7 | W25Q32JVSSIQ (32 Mbit) | `Memory_Flash:W25Q32JVSS` | `Package_SO:SOIC-8_5.3x5.3mm_P1.27mm` | C179173 | Extended |
| X1 | 50 MHz oscillator, 3.3 V | `Oscillator:ASE-xxxMHz` | `Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm` | C717684 | Extended |
| C64, C65 | 100nF 0402 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | C1525 | Basic |
| R16, R17, R18 | 4.7k 0402 | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | C25900 | Basic |

**Why these parts:**
- **Flash size:** the XC7A15T/35T bitstream is about 17.5 Mbit, and 32 Mbit holds it with room to spare.
- **Flash part:** I chose the cheaper W25Q32 over the W25Q128 you used on the carrier board. `openFPGALoader` can write it through the CH347.
- **Oscillator:** the one from your carrier board. It needs no capacitors and runs straight from 3.3 V.

## Connections, pin by pin

**U7 flash ↔ FPGA bank 14** (UG470 Master SPI wiring)

| Flash pin | FPGA ball | FPGA pin | Extra |
|---|---|---|---|
| 1 `~CS` | L12 | IO_L6P_T0_FCS_B_14 | R18 4.7k → +3V3 (keeps flash deselected) |
| 2 `DO/IO1` | J14 | IO_L1N_T0_D01_DIN_14 | |
| 3 `~WP/IO2` | K15 | IO_L2P_T0_D02_14 | R16 4.7k → +3V3 (UG470) |
| 5 `DI/IO0` | J13 | IO_L1P_T0_D00_MOSI_14 | |
| 6 `CLK` | `FLASH_CLK` label | from CCLK_0 in Section 4 | |
| 7 `~HOLD/IO3` | K16 | IO_L2N_T0_D03_14 | R17 4.7k → +3V3 (UG470) |
| 8 `VCC` | `+3V3` | | C64 100nF at the pin |
| 4 `GND` | `GND` | | |

**X1 oscillator**
- Pin 4 `Vdd` → `+3V3`, with C65 100nF. Pin 2 `GND` → GND.
- Pin 1 `EN` → `+3V3` (always on).
- Pin 3 `OUT` → U4A **N11** (IO_L13P_T2_MRCC_14). That's a clock-capable pin, so it can feed the PLL. Use a short wire or the local label `CLK50`.

**U4A power and straps**
- All 6 `VCCO_14` and all 6 `VCCO_15` → `+3V3`. Their capacitors are in Section 2.
- `PUDC_B` (L15, IO_L3P_T0_DQS_PUDC_B_14) → GND. This turns on the I/O pull-ups during configuration, so HyperRAM CS# and RESET# stay high. UG470 allows it tied straight to GND.

## Labels in this section

Shapes are from the **FPGA's** point of view.

| Global label | Shape | Direction | FPGA ball | Other end |
|---|---|---|---|---|
| `FLASH_CLK` | Input | Points **left** to Section 4 | (flash pin 6) | CCLK_0 |
| `UART_TX` | Output | Points **left** | T9 (IO_L22P_T3_A05_D21_14) | CH347 RXD1 |
| `UART_RX` | Input | Points **left** | T10 (IO_L22N_T3_A04_D20_14) | CH347 TXD1 |
| `HOST_SCK` | Input | Points **right** to Section 6 | A8 (IO_L2P_T0_AD8P_15) | J3 |
| `HOST_MOSI` | Input | right | A9 (IO_L2N_T0_AD8N_15) | J3 |
| `HOST_MISO` | Output | right | A10 (IO_L3N_T0_DQS_AD1N_15) | J3 |
| `HOST_CS_N` | Input | right | A12 (IO_L5N_T0_AD9N_15) | J3 |
| `HOST_RST_N` | Input | right | A13 (IO_L7P_T1_AD2P_15) | J3 |
| `HOST_START` | Input | right | A14 (IO_L7N_T1_AD2N_15) | J3 |
| `HOST_DONE` | Output | right | A15 (IO_L9N_T1_DQS_AD3N_15) | J3 |
| `HOST_PASS` | Output | right | B16 (IO_L10N_T1_AD11N_15) | J3 |
| `LED0` | Output | right | C16 (IO_L10P_T1_AD11P_15) | D2 |
| `LED1` | Output | right | D16 (IO_L17N_T2_A25_15) | D3 |
| `BTN_N` | Input | right | E16 (IO_L17P_T2_A26_15) | SW1 |

The test-host pins are all on the FPGA's outer row A/column 16, which is easiest to route on 4 layers. The SPI clock from the host is slow, so it doesn't need a clock-capable pin. Your RTL can sample it with the 50 MHz clock.

Leave all other I/O on U4A unconnected. I'll add their no-connect flags by script, as with Section 3.

## Bring-up test (after boards arrive)

1. Write a blink bitstream to flash: `openFPGALoader --cable ch347_jtag -f blink.bit`
2. Unplug and replug the board. It should boot from flash on its own and blink. This is PRD bring-up step 2.
3. Print a message over `UART_TX` and read it on the CH347 serial port. This is PRD step 3.

## Done-check

- [ ] Flash pins match the table: DI ↔ D00 (J13), DO ↔ D01 (J14), CS ↔ FCS_B (L12)
- [ ] 4.7k pull-ups on CS (R18), WP (R16) and HOLD (R17)
- [ ] X1 OUT → N11, EN → +3V3, C65 on Vdd
- [ ] PUDC_B (L15) → GND
- [ ] VCCO_14 ×6 and VCCO_15 ×6 → +3V3
- [ ] All 14 global labels on the listed balls
