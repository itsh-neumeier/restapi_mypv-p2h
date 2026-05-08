"""Constants for the myPV ELWA2 integration."""
from __future__ import annotations

DOMAIN = "restapi_mypv_p2h"

DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300

CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

ELWA2_DATA_KEYS = {
    "power": "power",
    "temp1": "temp1",
    "temp2": "temp2",
    "status": "status",
    "boost": "boost",
    "energy": "energy",
}

STATUS_OFF = 0
STATUS_RUNNING = 1
STATUS_ERROR = 2
