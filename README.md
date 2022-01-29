# jk-bms_grafana
Read data from a JK/Heltec BMS through RS-485 and graph it in Grafana.
This script is intended to be used with:
https://github.com/BarkinSpider/SolarShed/

# Pinout and connection

The JK BMS has an RS-485 port, but this is actually a TTL UART that gets turned into RS-485 with an optional converter, which in turn can be used with a RS-485 to USB converter. While this works, you don't need this whole chain. You can directly connect a TTL to USB converter to the TTL UART port. The pin-out on the connector:

```
RS485-TTL plug on BMS (4 Pins, JST 1.25mm pinch)
┌─── ─────── ────┐
│                │
│ O   O   O   O  │
│GND  RX  TX VBAT│
└────────────────┘
```
