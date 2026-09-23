# Changelog

## [Unreleased]

## [1.2.0] - 2026-09-23

### Added
- Neues Blueprint `victron_mppt_p2h_forecast_de.yaml`: prognosebasierte Freigabe (Victron-VRM-
  Tagesprognose + SOC als primäre Basis, MPPT-LIMITED nur noch sekundäre Nachregelung) statt
  festem SOC-Schwellwert. Heizstab bekommt weiterhin nie mehr als den real gemessenen
  PV-Überschuss zugewiesen; die Freigabe hängt vom berechneten Headroom (Resttagesprognose
  minus Energiebedarf bis Ziel-SOC minus Sicherheitsmarge) ab. Ergänzt, ersetzt nicht das
  bestehende SOC-Schwellwert-Blueprint. Die Akkukapazität für die Berechnung wird aus einem
  Ist-Ah-Sensor (z. B. Victron „battery capacity") über den aktuellen SOC hochgerechnet, nicht
  statisch eingegeben.

## [1.1.0] - 2026-09-22

### Fixed
- **Hassfest-Validierung schlug fehl**: `manifest.json` verwendete die Keys `icon` und
  `homeassistant`, die das aktuelle Hassfest-Schema für Custom Integrations nicht mehr kennt.
  `icon` entfernt (Icon kommt bereits über `icon.png`/`icon@2x.png`); Mindest-HA-Version zieht
  jetzt stattdessen `hacs.json` (`homeassistant`) heran, wie von HACS vorgesehen.
- **HACS-Validierung schlug fehl** („no valid topics"): GitHub-Repository-Topics ergänzt.
- **Options Flow (Einstellungen → Konfigurieren) stürzte immer ab** (`AttributeError:
  'MypvP2hOptionsFlow' object has no attribute 'config_entry'`). Das Scan-Interval war dadurch
  nachträglich nicht änderbar. `config_entry` wird jetzt korrekt im Konstruktor übernommen.
- **ENUM-Sensoren `warnings`/`upd_state` konnten beim Melden eines unbekannten/neuen
  Status-/Firmware-Codes abstürzen** (`ValueError: ... provides state value '999', which is not
  in the list of options`), da Home Assistant für ENUM-Sensoren nur deklarierte `options`-Werte
  als Zustand zulässt. Unbekannte Codes liefern jetzt den Zustand `unknown` statt des Rohwerts;
  der tatsächliche Rohcode bleibt zusätzlich über das Attribut `raw_value` einsehbar.
- Leistungsvorgabe (`number.target_power`) schlug bei einem Netzwerkfehler bisher stillschweigend
  fehl (nur Log-Eintrag, kein Fehler in der UI, `target_power` zeigte trotzdem den neuen Sollwert).
  Ein Fehler beim Senden an `/control.html` wird jetzt als Fehler an Home Assistant zurückgemeldet;
  der Keepalive versucht es weiterhin automatisch alle 5 s.
- Zu breite `except Exception`-Blöcke in Coordinator und Config Flow durch gezielte
  Netzwerk-/Timeout-/JSON-Fehlerbehandlung ersetzt, damit unerwartete Programmierfehler nicht
  mehr verschluckt werden.
- Veraltetes `FlowResult` aus `homeassistant.data_entry_flow` durch `ConfigFlowResult`
  (`homeassistant.config_entries`, mit Fallback für ältere HA-Versionen) ersetzt.
- `manifest.json`: `documentation`/`issue_tracker` verwiesen noch auf das alte Repository
  `ha-mypv-elwa2`, jetzt korrigiert auf `restapi_mypv-p2h`.
- README: Entity-Tabelle nannte nicht mehr existierende Entities (`energy_today`,
  `boost_active`, `error`) und fehlende aktuelle Sensoren; Scan-Interval-Bereich korrigiert
  (3–300 s statt 10–300 s); HACS-Installationslink korrigiert.

### Added
- Neuer Sensor `energy_consumption` (kWh, `device_class: energy`, `state_class:
  total_increasing`) für das Home-Assistant-Energiedashboard. Das Gerät liefert keinen
  Energiezähler; der Wert wird aus der gemessenen Ist-Leistung (`power_elwa2`) über die
  tatsächlich vergangene Zeit integriert und übersteht HA-Neustarts (`RestoreSensor`).
- Grundlegende `pytest`-Testsuite (Coordinator, Config Flow, Sensoren, Number) unter `tests/`.
- `ruff`-Konfiguration (`pyproject.toml`) und GitHub-Actions-Workflows für Lint/Tests sowie
  Hassfest-/HACS-Validierung.

## [1.0.15] - 2026-05-08

### Removed
- Sensors `power_solar`, `power_grid`, `surplus` — device does not provide independent PV/grid measurement; values duplicated heater power or were unavailable
- Binary sensors `boost_active` and `error` (block state) removed

### Changed
- `power_setpoint` ("Leistung (Ist)") moved from Diagnose to Sensoren section (removed DIAGNOSTIC entity category)

## [1.0.14] - 2026-05-08

### Changed
- `temp_ps` umbenannt: "Leistungsstufen-Temperatur" → "Geräte-Temperatur" / "Device temperature"

## [1.0.13] - 2026-05-08

### Added
- Sensor `upd_state` — Firmware-Update-Status (ENUM: Kein Update / Verfügbar / Lädt / Unterbrochen / Bereit)
- Sensor `warnings` — Gerätestatus/Fehlercode (ENUM, Klartextzuordnung DE+EN für alle Status-Codes aus Doku: STL, Übertemp, Sondenfehler, Hardwarefehler, Sensorfehler, Mainboard)
- Sensor `cur_ip` — Geräte-IP-Adresse (DIAGNOSTIC)

### Changed
- Gerät-Link ("Besuchen") öffnet jetzt direkt `/control.html` (Steuerungsseite)
- Hersteller in Geräteinfo: "my-PV GmbH"

## [1.0.12] - 2026-05-08

### Added
- Sensor `power_solar` — PV-Leistung vom Gerät gemessen (W)
- Sensor `power_grid` — Netzleistung (W, negativ = Einspeisung)
- Sensor `volt_mains` — Netzspannung (V, DIAGNOSTIC)
- Sensor `freq` — Netzfrequenz (Hz, skaliert aus mHz, DIAGNOSTIC)
- Sensor `temp_ps` — Leistungsstufen-Temperatur (°C, DIAGNOSTIC)
- `device_info.sw_version` aus `fwversion`-Feld (wird im Gerätepanel angezeigt)
- `device_info.model` korrigiert auf "AC ELWA 2"

## [1.0.11] - 2026-05-08

### Fixed
- Blueprint v2.1.1: MPPT-Zustandserkennung exakt `== 'LIMITED'` (Werte: OFF / ACTIVE / LIMITED); Description korrigiert

## [1.0.10] - 2026-05-08

### Changed
- Blueprint v2.1.0:
  - `solar_power_sensors` und `house_consumption_sensors` beide multi-select (Summe mehrerer Sensoren, z. B. 3 Phasen-Sensoren für Verbrauch)
  - `min_surplus_power` entfernt — Victron MPPT 450/200 regeln Produktion selbst herunter, fester Schwellwert verursacht Oszillation; SOC-Gate reicht
  - Surplus-Bedingung jetzt `surplus_w > 0` statt >= Schwellwert

## [1.0.9] - 2026-05-08

### Changed
- Blueprint `victron_mppt_p2h_dynamic_de.yaml` komplett überarbeitet (v2.0.0):
  - Separate Eingaben für Solarleistung und Hausverbrauch (statt vorberechnetem Überschuss-Sensor)
  - Anti-Limited-Regelung: schrittweise Leistungserhöhung wenn MPPT Limited → hält MPPT aus dem Drosselungsmodus
  - MPPT-Zustandserkennung case-insensitiv ("limit" / "begrenzt"), kompatibel mit allen Victron HA-Integrationen
  - Neuer Input `anti_limited_step` (Schrittweite beim Hochregeln, Standard 100 W)
  - Trigger reagiert sofort auf MPPT-Limited-Übergang (for: 5 s)

## [1.0.8] - 2026-05-08

### Fixed
- Brand assets in `brand/` folder (was `brands/`) — HACS and HA integration card now show logo and icon correctly
- Added `icon.png` / `icon@2x.png` directly in integration folder (required by HA)
- PNG icons generated from official my-PV logo

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
