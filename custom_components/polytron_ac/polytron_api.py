"""Polytron IoT API Client for Home Assistant."""
import urllib.request
import urllib.parse
import base64
import json
import ssl
import logging

_LOGGER = logging.getLogger(__name__)

class PolytronAPI:
    AUTH_BASE = "https://ism.fira.id"
    IOT_BASE = "https://ah.iot.polytron.co.id/rest/v5"
    USRSAPP_BASE = "https://usrsapp.iot.polytron.co.id"
    DEVSAPP_BASE = "https://devsapp.iot.polytron.co.id"

    GATEWAY_AUTH_FIRA = base64.b64encode(b"Smart_home:Smart_home132").decode()
    GATEWAY_AUTH_USRSAPP = base64.b64encode(b"usrsappUser:usrsappPass").decode()
    GATEWAY_AUTH_DEVSAPP = base64.b64encode(b"devsappUser:devsappPass").decode()

    def __init__(self, username: str, token: str, user_b: str = None):
        self.username = username
        self.token = token
        self.user_b = user_b
        self.ssl_ctx = ssl.create_default_context()

    @staticmethod
    def request_wa_otp(phone: str) -> dict:
        url = f"{PolytronAPI.AUTH_BASE}/api"
        payload = {
            "username": phone,
            "app_name": "smarthome",
            "app_action": "wa_otp",
            "app_language": "1",
            "sms_header": "<#> Polytron IOT",
            "sms_footer": ""
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Basic {PolytronAPI.GATEWAY_AUTH_FIRA}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/4.9.0"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def verify_otp(phone: str, otp_code: str) -> dict:
        url = f"{PolytronAPI.AUTH_BASE}/api"
        payload = {
            "username": phone,
            "otp_code": otp_code,
            "app_name": "smarthome",
            "app_action": "verify_otp",
            "app_language": "1"
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Basic {PolytronAPI.GATEWAY_AUTH_FIRA}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/4.9.0"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_devices(self) -> list:
        query = urllib.parse.urlencode({"uname": self.username, "token": self.token})
        url = f"{self.USRSAPP_BASE}/users/home?{query}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Basic {self.GATEWAY_AUTH_USRSAPP}",
            "Accept": "*/*",
            "User-Agent": "okhttp/4.9.0"
        })
        with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("devices", [])

    def get_live_state(self, serial: str, tz: str = "Asia/Jakarta") -> dict:
        query = urllib.parse.urlencode({
            "uname": self.username,
            "token": self.token,
            "sn": serial,
            "tz": tz
        })
        url = f"{self.DEVSAPP_BASE}/devices/home?{query}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Basic {self.GATEWAY_AUTH_DEVSAPP}",
            "Accept": "*/*",
            "User-Agent": "okhttp/4.9.0"
        })
        with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data.get("data", {})
            
            controls = {}
            for item in raw.get("con", []):
                e = item.get("enum")
                d = item.get("data")
                if e == "0":
                    controls["power"] = int(d) if d else 0
                elif e == "1":
                    controls["mode"] = int(d) if d else 2
                elif e == "3":
                    controls["target_temp"] = int(d) if d else 24
                elif e == "4":
                    controls["fan_speed"] = int(d) if d else 1
                elif e == "5":
                    controls["swing"] = int(d) if d else 0

            sensors = {}
            for item in raw.get("sen", []):
                e = item.get("enum")
                d = item.get("data")
                if e == "0" and d:
                    try:
                        sensors["room_temp"] = float(d) / 10.0 if len(d) == 3 else float(d)
                    except ValueError:
                        pass
                elif e == "1" and d:
                    try:
                        sensors["power_watt"] = float(d)
                    except ValueError:
                        pass
                elif e == "2" and d and item.get("hist") == "0":
                    try:
                        sensors["energy_kwh"] = float(d) / 1000.0
                    except ValueError:
                        pass

            # RSSI
            for item in raw.get("inf", []):
                if item.get("enum") == "7":
                    try:
                        sensors["rssi"] = int(item.get("data", 0))
                    except ValueError:
                        pass

            return {
                "serialNumber": serial,
                "controls": controls,
                "sensors": sensors
            }

    def send_control(self, serial: str, enum_id: int, dtyp: int, data_val: int) -> bool:
        url = f"{self.DEVSAPP_BASE}/devices/control"
        payload = {
            "uname": self.username,
            "token": self.token,
            "sn": serial,
            "enum": str(enum_id),
            "dtyp": str(dtyp),
            "data": str(data_val)
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Basic {self.GATEWAY_AUTH_DEVSAPP}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "okhttp/4.9.0"
        })
        with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res.get("errc") == "0"
