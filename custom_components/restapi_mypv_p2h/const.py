"""Constants for the myPV P2H integration."""
from __future__ import annotations

DOMAIN = "restapi_mypv_p2h"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 3
MAX_SCAN_INTERVAL = 300

CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

ELWA2_DATA_KEYS = {
    "power": "power_elwa2",
    "temp1": "temp1",
    "temp2": "temp2",
    "boost": "boostactive",
    "surplus": "surplus",
    "block": "blockactive",
    "ctrlstate": "ctrlstate",
    "power_solar": "power_solar",
    "power_grid": "power_grid",
    "volt_mains": "volt_mains",
    "freq": "freq",
    "temp_ps": "temp_ps",
    "upd_state": "upd_state",
    "warnings": "warnings",
    "cur_ip": "cur_ip",
}

STATUS_BLOCK = 1
