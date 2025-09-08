import json
#import demjson3
import json5

from bs4 import BeautifulSoup

from curl_cffi import requests as cureq
import stealth_requests as requests
#import cloudscraper

import Ip_Manager

import time
import random

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
    "Connection": "keep-alive"
}

class Web_Getter:

    __bot_text = ""

    def __init__(self, ssid, bot_text):
        self.__bot_text = bot_text
        Ip_Manager.target_ssid = ssid

    def get_html(self, url_link: str) -> BeautifulSoup:
        """
            Fetches the HTML content of a URL using a mobile-mimicking session, handling connection
            errors and anti-bot detection by retrying with refreshed IPs. Returns a BeautifulSoup object.
        """
        session = cureq.Session(impersonate="chrome120", headers=headers)
        Ip_Manager.reconnect_to_mobile()
        while True:
            try:
                resp = session.get(url_link).text
            except Exception as e:
                print(f".GET ERROR (trying to connect to ssid): {e}")
                Ip_Manager.reconnect_to_mobile()
                continue
            if self.__bot_text in resp:
                print("BOT DETECTED .. attempting to refresh")
                # pretty sure we need to wait until our ip refreshes
                time.sleep(20)
                continue
            return BeautifulSoup(resp, 'html.parser')


    def get_json_api(self, url_link: str, referer: str) -> dict:
        """
            Fetches JSON data from the given URL, handling connection errors by reconnecting IP.
            Returns the parsed JSON as a Python dictionary.
        """
        Ip_Manager.reconnect_to_mobile()
        #headers["referer"] = referer
        #session = cureq.Session(impersonate="chrome120", headers=headers)
        #resp = requests.get(url_link).text_content()
        while True:
            try:
                resp = requests.get(url_link).text_content()
                #return json.loads(resp)
                return json.loads(resp)
            except Exception as e:
                print(f".GET ERROR (trying to connect to ssid): {e}")
                print(resp)
                exit()
                Ip_Manager.reconnect_to_mobile()