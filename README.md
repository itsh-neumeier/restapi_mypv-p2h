# myPV P2H — Home Assistant Integration

Lokale Home Assistant Integration für den myPV P2H Heizstab.
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
- myPV P2H im gleichen Netzwerk erreichbar

## Installation

### HACS (empfohlen)

1. HACS → Custom Repositories → `https://github.com/itsh-neumeier/ha-mypv-elwa2` → Typ: Integration
2. Integration suchen: **myPV P2H** → Installieren
3. HA neu starten

### Manuell

1. `custom_components/restapi_mypv_p2h` nach `config/custom_components` kopieren
2. Neu starten

## Konfiguration

**Einstellungen → Geräte & Dienste → Integration hinzufügen → myPV P2H**

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

## Blueprint – Dynamische PV-Überschuss-Steuerung

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fitsh-neumeier%2Frestapi_mypv-p2h%2Fmaster%2Fblueprints%2Fautomation%2Fenergy%2Fvictron_mppt_p2h_dynamic_de.yaml)

Passt die Leistung des Heizstabs dynamisch dem PV-Überschuss an (50 W-Schritte, max. 3500 W).
Schaltet bei Erreichen der Zieltemperatur ab. Freigabe über Victron MPPT LIMITED-Modus und/oder Batterie-SOC.

| Parameter | Beschreibung |
|-----------|-------------|
| Leistungsvorgabe (number) | `number.target_power` der Integration |
| PV-Überschuss-Sensor | Sensor mit Überschuss in Watt |
| Temperatursensor | `sensor.temperature_1` oder `sensor.temperature_2` |
| Zieltemperatur | Abschalttemperatur in °C (Standard: 60 °C) |
| Minimaler Überschuss | Mindest-Überschuss für Aktivierung (Standard: 200 W) |
| Batterie-SOC-Sensor | Ladestand-Sensor |
| MPPT-Betriebsmodus | Victron MPPT Sensor(en) |
| Freigabemodus | LIMITED + SOC / Nur LIMITED / Nur SOC |
