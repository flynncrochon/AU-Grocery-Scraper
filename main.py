from Coles_Scraper import Coles_Scraper
import tkinter as tk
import csv

#
# open a coles session using ssid as a sample proxy
#
if __name__ == "__main__":
    # ssid = "OnePlus 12"
    ssid = "I-dont-know"
    coles_session = Coles_Scraper(ssid)
    coles_session.scrape_all_inner_categories()