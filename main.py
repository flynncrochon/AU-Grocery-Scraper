from Coles_Scraper import Coles_Scraper
import tkinter as tk
import csv

#
# open a coles session using ssid as a sample proxy
#
ssid = "OnePlus 12"
#ssid = "I-dont-know"
coles_session = Coles_Scraper(ssid)
coles_session.scrape_all_inner_categories()

#import stealth_requests as requests
#resp = requests.get("https://www.coles.com.au/_next/data/20250902.7-6731b0fd75ad003810a8d0b7573f54185cabaa61/en/browse/meat-seafood.json?slug=meat-seafood&page=5")

#print(resp.text_content())