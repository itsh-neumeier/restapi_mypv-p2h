# myPV ELWA2 — Home Assistant Integration

Lokale Home Assistant Integration für den myPV ELWA2 Heizstab.
Liest Gerätedaten per HTTP-Polling und erlaubt die Leistungsvorgabe (0–3500 W) direkt aus HA.

## Features

- Leistungsvorgabe als `number`-Entity (0–3500 W, Slider)
- Temperatursensoren (Sensor 1 + 2)
- Tagesenergie in kWh
- Boost-Modus und Fehler-Status als Binary Sensor
- Konfigurierbares Polling-Intervall (10–300 s)
- Kein Cloud-Zwang, vollständig lokal

## Requirements

- Home Assistant ≥ 2024.1
- myPV ELWA2 im gleichen Netzwerk erreichbar

## Installation

### HACS (empfohlen)

1. HACS → Custom Repositories → `https://github.com/itsh-neumeier/ha-mypv-elwa2` → Typ: Integration
2. Integration suchen: **myPV ELWA2** → Installieren
3. HA neu starten

### Manuell

1. `custom_components/restapi_mypv_p2h` nach `config/custom_components` kopieren
2. Neu starten

## Konfiguration

**Einstellungen → Geräte & Dienste → Integration hinzufügen → myPV ELWA2**

| Parameter       | Default | Beschreibung                  |
|-----------------|---------|-------------------------------|
| Host            | —       | IP-Adresse des ELWA2          |
| Scan Interval   | 30      | Abfrageintervall in Sekunden  |

## Entities

| Entity           | Typ            | Einheit | Beschreibung               |
|------------------|----------------|---------|----------------------------|
| `power_setpoint` | sensor         | W       | Aktuell gesetzte Leistung  |
| `temperature_1`  | sensor         | °C      | Temperatur Sensor 1        |
| `temperature_2`  | sensor         | °C      | Temperatur Sensor 2        |
| `energy_today`   | sensor         | kWh     | Tagesenergie               |
| `boost_active`   | binary_sensor  | —       | Boost-Modus aktiv          |
| `error`          | binary_sensor  | —       | Gerätefehler               |
| `target_power`   | number         | W       | Leistungsvorgabe 0–3500 W  |
