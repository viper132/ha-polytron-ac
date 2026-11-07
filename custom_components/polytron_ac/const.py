"""Constants for the Polytron Smart AC integration."""

DOMAIN = "polytron_ac"

CONF_USERNAME = "username"
CONF_TOKEN = "token"
CONF_USER_B = "user_b"

DEFAULT_NAME = "Polytron AC"
SCAN_INTERVAL_SECONDS = 15

# Supported HVAC modes mapping
HVAC_MODE_TO_POLYTRON = {
    "cool": 2,
    "dry": 3,
    "fan_only": 1,
    "auto": 4,
}

POLYTRON_TO_HVAC_MODE = {
    1: "fan_only",
    2: "cool",
    3: "dry",
    4: "auto",
}

# Fan modes mapping
FAN_MODE_TO_POLYTRON = {
    "low": 0,
    "auto": 1,
    "medium": 2,
    "high": 3,
}

POLYTRON_TO_FAN_MODE = {
    0: "low",
    1: "auto",
    2: "medium",
    3: "high",
}
