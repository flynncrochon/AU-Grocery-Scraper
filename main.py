from Coles_Scraper import Coles_Scraper

# open a coles session using ssid as a sample proxy
#
ssid = "sample_ssid"
coles_session = Coles_Scraper(ssid)
coles_session.scrape_all_inner_categories()
