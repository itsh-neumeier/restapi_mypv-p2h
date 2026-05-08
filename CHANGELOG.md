# Changelog

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
