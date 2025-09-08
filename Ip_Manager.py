from winwifi import WinWiFi
import subprocess

target_ssid = ""
def get_current_ssid():
    """
    Returns the SSID of the currently connected Wi-Fi network on Windows.
    If it cannot be determined (e.g., no connection), returns None.
    """
    try:
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"], text=True
        )
        for line in result.splitlines():
            if "SSID" in line and "BSSID" not in line:
                return line.split(":", 1)[1].strip()
    except:
        return None

def reconnect_to_mobile():
    """
    Attempts to reconnect the PC to the target Wi-Fi (mobile hotspot) until successful,
    retrying on failure and printing the attempt number.
    """
    attempt_num = 1
    while get_current_ssid() != target_ssid:
        print(f"Attempt ({attempt_num}) to connect to: {target_ssid}")
        try:
            WinWiFi.disconnect()
            WinWiFi.connect(target_ssid)
        except:
            attempt_num += 1
            continue
