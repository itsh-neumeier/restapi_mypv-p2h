# Changelog

## [1.0.7] - 2026-05-08

### Fixed
- Integration card title is now "myPV P2H" (was "myPV P2H (host)")

## [1.0.6] - 2026-05-08

### Changed
- `target_power` number entity shows only the HA-internal setpoint (`_target_power`), not the device-reported value — clear Soll/Ist separation
- `power_setpoint` sensor renamed to "Leistung (Ist)" / "Power (actual)" — shows device-reported actual power
- `target_power` renamed to "Leistungsvorgabe (Soll)" / "Target power (setpoint)"
- Minimum scan interval reduced from 10 s to 3 s (≥ 2500 ms)

### Added
- `brands/logo.png` — official my-PV logo (HA 2026.3 custom brands support)
- `brands/icon.svg` — official my-PV hot water / P2H icon (from my-pv.com)
- `manifest.json`: `"icon": "mdi:water-boiler"` fallback (HA 2026.3)

## [1.0.5] - 2026-05-08

### Fixed
- `power_elwa2` correct API field name (was `power` — does not exist in device response)
- `boostactive` correct field name (was `boost`)
- `blockactive` correct field name for error/block state (was `status` — does not exist)
- `surplus` marked optional (null when no myPV meters configured)
- `temperature_2` marked optional (not all firmware versions expose it)

### Added
- `control_state` diagnostic sensor (device ctrlstate string, e.g. "No Control", "Heat")
- Config flow description: HTTP control must be enabled in device web interface

### Removed
- `energy_today` sensor (field does not exist in device API)

## [1.0.4] - 2026-05-08

### Fixed
- `target_power` shows "unknown" when device does not return `power` field — falls back to last sent value
- `target_power` UI mode changed from slider to input box

## [1.0.3] - 2026-05-08

### Added
- Blueprint `victron_mppt_p2h_dynamic_de.yaml`: dynamic power control based on PV surplus with temperature cutoff

## [1.0.2] - 2026-05-08

### Changed
- Rename integration display name from "myPV ELWA2" to "myPV P2H" (Power to Heat)

## [1.0.1] - 2026-05-08

### Fixed
- Temperature sensors divided by 10 (device reports values as tenths of °C)
- Power keepalive: resends setpoint every 5 s so device does not drop to 0 W after 10 s

## [1.0.0] - 2026-05-08

### Added
- Initial release
- Sensors: `power_setpoint`, `temperature_1`, `temperature_2`, `energy_today`
- Binary sensors: `boost_active`, `error`
- Number: `target_power` (0–3500 W, slider)
- Config Flow with connection test and OptionsFlow for scan interval
