# JK BMS to Grafana
Read data from a JK BMS through RS-485 and graph it in Grafana.
This script is intended to be used with:
https://github.com/BarkinSpider/SolarShed/

The JK BMS can be found on AliExpress and other sites, for example: https://s.click.aliexpress.com/e/_DBEzZwv or https://s.click.aliexpress.com/e/_oCQ9mP3

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

To prevent issues, ground loops (the GND pin connects directly to battery negative), and other problems, you should use an isolated UART/USB converter or isolated UART/UART if you connect this directly to another microcontroller. Failing that, use a USB to USB isolator like this one (based on an ADuM3160): https://s.click.aliexpress.com/e/_onvOeBT if you connect to USB on an R-Pi or something. If you want to connect more than one UART/USB converter, you can also find these isolators as a USB Hub with four ports: https://s.click.aliexpress.com/e/_oFScxdF

See this post on DIY Solar Forum for the locaton of this port on various versions of the BMS:
https://diysolarforum.com/threads/victron-venusos-driver-for-serial-connected-bms-llt-jbd-daly-smart-ant-jkbms-heltec-renogy.17847/post-424921
