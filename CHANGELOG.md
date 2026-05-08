# Changelog

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
