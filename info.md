# Huawei SUN2000

A Home Assistant integration for Huawei SUN2000 L1 residential inverters and
their LUNA2000 batteries, over Modbus TCP.

- Reads PV, grid, yield and battery telemetry
- Writes the curated battery controls: power limits, charge/discharge cutoffs,
  working mode, forced charge/discharge and grid charging
- Shares Home Assistant's `modbus` connection
- Works with or without a battery, and with firmware that lacks the advanced
  forced-charge registers
- Keeps lifetime energy sensors available through the nightly inverter shutdown

Default connection: port `8899`, unit ID `1`.

See the README for the full entity list and installation instructions.
