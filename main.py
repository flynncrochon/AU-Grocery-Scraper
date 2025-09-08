from Coles_Scraper import Coles_Scraper

if __name__ == "__main__":
    ssid = ""
    coles_session = Coles_Scraper(ssid)
    coles_session.scrape_all_inner_categories()

