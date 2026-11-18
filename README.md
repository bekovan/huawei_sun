# Huawei SUN2000

A Home Assistant integration for Huawei SUN2000 L1 residential inverters and
the LUNA2000 battery that hangs off them.

The integration talks Modbus TCP through Home Assistant's own `modbus`
integration, so the connection is shared with anything else that talks to the
same device and is released automatically when the entry unloads.

## Supported hardware

Written against the **SUN2000-3.68KTL-L1** with an optional **LUNA2000**
battery, at unit ID 1 and the Huawei default Modbus TCP port `8899`.

Other L1 models serve the same holding-register map and should work. The
battery blocks are optional: an inverter without a LUNA2000 sets up fine and
simply creates no battery entities. The advanced forced charge/discharge
registers (`47246`–`47249`) are optional too, so older firmware keeps the
battery power limits, cutoffs and working mode without them. The external grid
meter block (`37100`–`37138`) is optional as well: an inverter without one
creates no Power meter device or meter entities.

Only the registers this integration exposes are declared. Adding another
register means adding a field to the register map and wiring it into a
platform.

## Installation

Requires Home Assistant 2026.6.0 or newer.

### HACS

1. Add `https://github.com/bekovan/ha-huawei-sun` as a custom repository
   (category: Integration).
2. Install **Huawei SUN2000**.
3. Restart Home Assistant.
4. Add the integration and enter the inverter's address

### Manual

Copy `custom_components/huawei_sun` into your Home Assistant
`config/custom_components` directory and restart.

## Configuration

The config flow asks for three things:

| Field | Default | Notes |
|---|---|---|
| Host | — | IP address or hostname of the inverter or its Modbus bridge |
| Port | `8899` | Huawei's Modbus TCP port |
| Unit ID | `1` | Modbus unit (slave) ID |

The flow reads the model and serial number once to prove the device answers,
then uses the serial number as the unique ID, falling back to
`host-port-unit_id` when the inverter reports none. The polling interval is set
in the integration's options (default 30 s, minimum 5 s, maximum 3600 s).

Modbus TCP must be enabled on the inverter. On a SUN2000 that is done in the
installer menu (`Communication configuration` → `Modbus TCP`), and only one
Modbus client may hold the connection at a time.

## Entities

Entities are grouped into three devices. The inverter is the parent; the
**LUNA2000** battery and **Power meter** are separate child devices linked to
it with `via_device_id`.

### Inverter

- PV string voltage and current (2 strings)
- Input power, active and reactive power, power factor, grid frequency
- Phase voltages and currents
- Efficiency and internal temperature
- Device status (decoded running state)
- Total, daily, monthly and yearly yield
- Problem binary sensor (alarm words plus battery fault)
- Active power limit (writable, %, register `40125`)

### Battery (LUNA2000)

The battery appears as its own **LUNA2000** device linked to the inverter.

- State of charge, charge/discharge power, bus voltage and current
- Battery temperature, running status and the working mode the unit reports
- Rated charge/discharge power, daily and lifetime charge/discharge energy
- Rated capacity
- Battery connected binary sensor

### Writable battery settings

| Entity | Register | Notes |
|---|---|---|
| Maximum charging power | `47075` | W |
| Maximum discharging power | `47077` | W |
| Charging cutoff state of charge | `47081` | % |
| Discharging cutoff state of charge | `47082` | % |
| Grid charge cutoff state of charge | `47088` | % |
| Grid charge maximum power | `47244` | W, 0–20000, step 100 |
| Peak Shaving SOC | `47955` | %, 0–100, step 0.1; optional block |
| Forced charge/discharge period | `47083` | min |
| Forced target state of charge | `47101` | % |
| Working mode | `47086` | Adaptive … Third-party control. Writable, and distinct from the read-only *Battery working mode* sensor at `37006` |
| Forced charge/discharge | `47100` | Stop / Charge / Discharge |
| Charge from grid | `47087` | on / off |
| Forced end condition | `47246` | Time / State of charge (optional block) |
| Forced charge power | `47247` | W (optional block) |
| Forced discharge power | `47249` | W (optional block) |

Time-of-use and peak-shaving *schedules* are deliberately **not** implemented:
they are large tables that are easy to corrupt and are better edited in the
Huawei app or FusionSolar. The single peak-shaving reserve at `47955` is exposed
as a number when the inverter serves that register.

Every write is bounds-checked in the vendored device library before it reaches
the inverter, so a service call cannot store a nonsensical value.

### Power meter (optional)

When the inverter answers on registers `37100`–`37138`, the external grid meter
is exposed as its own **Power meter** device:

- Enabled by default: Active power, Power factor, Exported energy, Imported
  energy
- Disabled by default (enable them in the entity settings): meter status and
  type, phase A/B/C voltage, current and power, line voltages A–B/B–C/C–A,
  reactive power, grid frequency and reactive energy

Exported energy is normalised with `abs()` because Huawei can report the raw
counter as a negative value. Active power keeps its sign, so a negative value
means export.

## Design notes

- Telemetry at `32xxx`, the inverter's active power limit at `40125` and the
  battery settings at `47xxx` are all read with holding registers (function
  code 3), which is what Huawei serves them from.
- The LUNA2000 and Power meter are separate devices linked to the inverter with
  `via_device_id`. The split did not change any entity ID or unique ID.
- The battery, the inverter settings block, the advanced forced settings, the
  peak-shaving block and the grid meter are probed once with `read_optional`. A
  block the firmware rejects becomes `None`, and no entities are created for it.
- Lifetime energy sensors restore their last value, so a nightly inverter
  shutdown does not punch a hole in long-term statistics.
- The vendored `vendor/huawei_modbus` package imports no Home Assistant module;
  it only needs a `modbus_connection` unit, so it can be tested on its own.

## Diagnostics

**Settings → Devices & Services → Huawei SUN2000 → Download diagnostics**
returns the entry data and options, the identity block, whether a battery is
present, the outcome of the last poll (`last_update_success`, the blocks that
refreshed, the blocks that failed with their errors, and any error from the raw
register read) and every register this integration reads. The host, inverter
serial number and battery serial number are redacted.

## Credits

Structure based on [integration_blueprint](https://github.com/ludeeus/integration_blueprint)
by Joakim Sørensen. Register addresses and scale factors were cross-checked
against the community [huawei-solar](https://github.com/wlcrs/huawei-solar-lib)
library.

## License

MIT
