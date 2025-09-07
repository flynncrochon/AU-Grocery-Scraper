from winwifi import WinWiFi
import subprocess
import time

target_ssid = "OnePlus 12"

def get_current_ssid():
    try:
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"], text=True
        )
        for line in result.splitlines():
            if "SSID" in line and "BSSID" not in line:
                return line.split(":", 1)[1].strip()
    except Exception as e:
        return None
def reconnect_to_mobile():
    attempt_num = 1
    while get_current_ssid() != target_ssid:
        print(f"Attempt ({attempt_num}) to connect to: {target_ssid}")
        try:
            WinWiFi.connect(target_ssid)
        except:
            attempt_num = attempt_num + 1
            continue
