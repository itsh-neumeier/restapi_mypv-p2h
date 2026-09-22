# myPV P2H — Home Assistant Integration

Lokale Home Assistant Integration für my-PV Power-to-Heat-Geräte.
Liest Gerätedaten per HTTP-Polling und erlaubt die Leistungsvorgabe (0–3500 W) direkt aus HA —
vollständig lokal, ohne Cloud-Zwang.

## Unterstützte Geräte

- **my-PV AC ELWA 2** — aktuell einziges getestetes und unterstütztes Gerät

Andere my-PV P2H-Geräte (z. B. AC THOR) werden derzeit nicht unterstützt, da API-Endpunkte
und Steuerbereich abweichen können.

## Voraussetzungen

- Home Assistant ≥ 2024.1
- Gerät im gleichen Netzwerk erreichbar
- **Steuerungsart im Gerät-Webinterface auf „HTTP" gestellt** (sonst schlägt die Einrichtung
  mit „Cannot connect to device" fehl)

## Features

- Leistungsvorgabe als `number`-Entity (0–3500 W, 50-W-Schritte)
- Automatischer Keepalive: Solange die Zielleistung > 0 W ist, wird der Sollwert alle 5 s
  erneut an das Gerät gesendet, damit es die Vorgabe nicht wegen Timeout verwirft
- Temperatur-, Netz- und Diagnosesensoren (siehe Entity-Tabelle)
- Energieverbrauch als `sensor.energy_consumption` (kWh, `total_increasing`) für das
  Home-Assistant-Energiedashboard — aus der gemessenen Ist-Leistung berechnet
- Konfigurierbares Abfrageintervall (3–300 s, Standard 30 s), nachträglich über Optionen änderbar
- Kein Cloud-Zwang, vollständig lokal (`local_polling`)

## Installation

### HACS (empfohlen)

1. HACS → Custom Repositories → `https://github.com/itsh-neumeier/restapi_mypv-p2h` → Typ: Integration
2. Integration suchen: **myPV P2H** → Installieren
3. HA neu starten

### Manuell

1. `custom_components/restapi_mypv_p2h` nach `config/custom_components` kopieren
2. Neu starten

## Konfiguration

**Einstellungen → Geräte & Dienste → Integration hinzufügen → myPV P2H**

| Parameter       | Default | Beschreibung                                    |
|-----------------|---------|--------------------------------------------------|
| Host            | —       | IP-Adresse des Geräts                            |
| Scan Interval   | 30      | Abfrageintervall in Sekunden (3–300)              |

Das Abfrageintervall kann nachträglich über **Einstellungen → Geräte & Dienste → myPV P2H →
Konfigurieren** (Options Flow) geändert werden, ohne die Integration neu einzurichten. Eine
Änderung der IP-Adresse erfordert derzeit das Entfernen und Neuanlegen der Integration (siehe
Bekannte Einschränkungen).

## Entities

Alle Entities werden einem gemeinsamen Gerät zugeordnet. Optionale Sensoren werden nur verfügbar
angezeigt, wenn Gerät/Firmware den jeweiligen Datenpunkt tatsächlich liefert.

| Entity (Key)     | Typ    | Einheit | Kategorie | Beschreibung                                  |
|------------------|--------|---------|-----------|------------------------------------------------|
| `target_power`   | number | W       | —         | Leistungsvorgabe (Soll), 0–3500 W, 50-W-Schritte |
| `power_setpoint` | sensor | W       | —         | Leistung (Ist)                                |
| `energy_consumption` | sensor | kWh | —      | Energieverbrauch (kumuliert, für Energiedashboard) |
| `temperature_1`  | sensor | °C      | —         | Temperatur Sensor 1                           |
| `temperature_2`  | sensor | °C      | —         | Temperatur Sensor 2 (optional)                 |
| `control_state`  | sensor | —       | Diagnose  | Steuerstatus (optional)                        |
| `volt_mains`     | sensor | V       | Diagnose  | Netzspannung (optional)                        |
| `freq`           | sensor | Hz      | Diagnose  | Netzfrequenz (optional)                        |
| `temp_ps`        | sensor | °C      | Diagnose  | Geräte-Temperatur (optional)                   |
| `upd_state`      | sensor | —       | Diagnose  | Firmware-Update-Status, ENUM (optional)        |
| `warnings`       | sensor | —       | Diagnose  | Gerätestatus/Fehlercode, ENUM (optional)       |
| `cur_ip`         | sensor | —       | Diagnose  | Geräte-IP-Adresse (optional)                   |

„Optional" bedeutet: Der Sensor liefert `unbekannt`, solange die Firmware diesen Datenpunkt
nicht bereitstellt. Meldet das Gerät bei `upd_state`/`warnings` einen noch nicht bekannten
Code (z. B. durch neue Firmware), zeigt der Sensor den Zustand `unknown` statt abzustürzen;
der tatsächliche Rohcode bleibt über das Entity-Attribut `raw_value` sichtbar.

`energy_consumption` liefert das Gerät **nicht** direkt (die API kennt keinen Energiezähler,
nur die Momentanleistung `power_elwa2`). Die Integration berechnet den kWh-Wert daher selbst
durch Aufsummieren der gemessenen Ist-Leistung über die tatsächlich vergangene Zeit zwischen
zwei Abfragen. Genauigkeit hängt entsprechend vom Abfrageintervall ab (kürzeres Intervall =
genauer). Der Zählerstand übersteht HA-Neustarts; während eines Geräteausfalls wird nicht
weitergezählt, der Sensor zeigt dann „nicht verfügbar" statt eines geschätzten Wertes.

## Energiedashboard einbinden

`sensor.energy_consumption` kann direkt unter **Einstellungen → Dashboards → Energie →
Geräte hinzufügen** ausgewählt werden (erfüllt die dortigen Anforderungen: `device_class:
energy`, `state_class: total_increasing`, Einheit kWh). Kein zusätzlicher Helper nötig.

## Update-/Polling-Verhalten

- Gerätedaten (`/data.jsn`) werden alle *Scan Interval* Sekunden abgefragt (Standard 30 s).
- Sobald eine Zielleistung > 0 W gesetzt wird, sendet die Integration **unabhängig vom Scan
  Interval** zusätzlich alle 5 Sekunden einen Keepalive an `/control.html`. Der Keepalive
  stoppt automatisch bei 0 W, beim Entladen der Integration oder beim Neuladen des Config Entry.

## Troubleshooting

- **„Cannot connect to device" beim Einrichten**: IP/Host prüfen, Gerät im selben Netzwerk
  erreichbar? Steuerungsart im Gerät-Webinterface auf HTTP gestellt?
- **Leistungsvorgabe wird nicht übernommen**: Home-Assistant-Log auf `Failed to set power on
  myPV P2H` prüfen — deutet auf ein Netzwerk-/Erreichbarkeitsproblem hin. Die Integration
  versucht es per Keepalive weiterhin alle 5 s, sobald das Gerät wieder erreichbar ist.
- **Ein Sensor fehlt oder bleibt „nicht verfügbar"**: Mehrere Sensoren sind optional und
  hängen von Gerätemodell/Firmware ab (siehe Entity-Tabelle oben).

## Bekannte Einschränkungen

- Aktuell wird nur der **my-PV AC ELWA 2** unterstützt.
- Keine Geräte-Authentifizierung implementiert.
- Kein Reconfigure Flow — eine Änderung der Host-/IP-Adresse erfordert das Entfernen und
  Neuanlegen der Integration; das Abfrageintervall lässt sich dagegen über die Optionen ändern.

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
