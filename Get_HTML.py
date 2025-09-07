#import cloudscraper
from curl_cffi import requests as cureq
import Ip_Manager
import time
import random
from bs4 import BeautifulSoup

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/605.1.15 Chrome/139.0.0.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 Chrome/139.0.0.0 Mobile Safari/537.36",
    # add more
]

headers = {
    "User-Agent": random.choice(user_agents),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

class Get_HTML:
    def __init__(self, ssid, bot_text):
        self.__bot_text = bot_text
        Ip_Manager.target_ssid = ssid

    __bot_text = ""

    def get(self, url_link):
        session = cureq.Session(impersonate="chrome120", headers=headers)
        Ip_Manager.reconnect_to_mobile()
        resp = ""
        while True:
            try:
                resp = session.get("https://www.coles.com.au/browse").text
                if "As you were browsing something about your browser made us think you were a bot" in resp:
                    print("BOT DETECTED .. attempting to refresh")
                    time.sleep(5)
                    continue
                return BeautifulSoup(resp, 'html.parser')
            except:
                print(".GET ERROR (trying to connect to ssid)")
                Ip_Manager.reconnect_to_mobile()
