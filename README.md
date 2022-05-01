# JK BMS to Grafana
Read data from a JK/Heltec BMS through RS-485 and graph it in Grafana.
This script is intended to be used with:
https://github.com/BarkinSpider/SolarShed/

Alternatively, a set-up for this is documented here for both Raspberry Pi and plain Debian or derivatives:
https://diysolarforum.com/ewr-carta/data_communication/

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

See this post on DIY Solar Forum for the locaton of this port on various versions of the BMS:
https://diysolarforum.com/threads/victron-venusos-driver-for-serial-connected-bms-llt-jbd-daly-smart-ant-jkbms-heltec-renogy.17847/post-424921
