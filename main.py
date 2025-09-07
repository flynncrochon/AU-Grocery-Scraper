from operator import truediv

from curl_cffi import requests as cureq
import pickle
from bs4 import BeautifulSoup
import json
import pandas as pd
import math
import json
import time
#import cloudscraper
import random
import ip_manager


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

class Coles_Scrapper:

    coles_categories = []
    total_product_df = pd.DataFrame(
        columns=["prodid", "brand", "name", "size", "currentprice", "fullprice", "salespercentage", "rawdescription"])
    total_hier_df = pd.DataFrame(
        columns=["prodid", "aisle", "category", "subcategory", "aisleid", "categoryid", "subcategoryid"])
    build_id = "0"

    def scrape_all_categories(self):

        session = cureq.Session(impersonate="chrome120", headers = headers)
        ip_manager.reconnect_to_mobile()
        resp = ""
        while True:
            try:
                resp = session.get("https://www.coles.com.au/browse").text
                break
            except:
                print(".GET ERROR (trying to connect to ssid)")
                ip_manager.reconnect_to_mobile()

        soup = BeautifulSoup(resp, 'html.parser')
        json_data = {}
        try:
            next_data = soup.find('script', id='__NEXT_DATA__')
            json_data = json.loads(next_data.string)
        except Exception as e:
            print(resp)
            exit()

        build_id = json_data["buildId"]
        print(build_id)
        categories = json_data["props"]["pageProps"]["allProductCategories"]["catalogGroupView"]
        return_cat = []
        for cat in categories:
            return_cat.append(cat["seoToken"])
            print(cat["id"], " - ", cat["seoToken"])

        self.coles_categories = return_cat
        self.build_id = build_id

    def scrape_inner_category(self, seo_code):
        cur_page = 1
        while True:

            print(f"https://www.coles.com.au/browse/{seo_code}?page={cur_page}")
            # this below link is weird
            #print(f"https://www.coles.com.au/_next/data/{self.build_id}/en/browse/{seo_code}.json?slug={seo_code}?page={cur_page}")

            time.sleep(2)
            ip_manager.reconnect_to_mobile()
            session = cureq.Session(impersonate="chrome120", headers=headers)
            #scraper = cloudscraper.create_scraper()
            resp = ""
            while True:
                try:
                    #resp = scraper.get(f"https://www.coles.com.au/_next/data/{self.build_id}/en/browse/{seo_code}.json?slug={seo_code}?page={cur_page}").text
                    resp = session.get(f"https://www.coles.com.au/browse/{seo_code}?page={cur_page}").text
                    break
                except:
                    print(".GET ERROR (trying to connect to ssid)")
                    ip_manager.reconnect_to_mobile()

            soup = BeautifulSoup(resp, 'html.parser')
            # Find the script tag with id="__NEXT_DATA__"
            next_data = soup.find('script', id='__NEXT_DATA__')


            json_data = {}
            try:
                json_data = json.loads(next_data.string)
            except Exception as e:
                print("error")
                if "As you were browsing something about your browser made us think you were a bot" in resp:
                    print("BOT DETECTED .. attempting to refresh")
                    time.sleep(5)
                    continue

                print(resp)

                exit()

            products = json_data["props"]["pageProps"]["searchResults"]["results"]
            print(f"debug 1 {json_data["props"]["pageProps"]["searchResults"]["noOfResults"]}")
            print(f"debug 2 {json_data["props"]["pageProps"]["searchResults"]["pageSize"]}")
            num_of_pages = json_data["props"]["pageProps"]["searchResults"]["noOfResults"] / json_data["props"]["pageProps"]["searchResults"]["pageSize"]
            num_of_pages = math.ceil(num_of_pages)
            if json_data["props"]["pageProps"]["searchResults"]["pageSize"] < 48:
                print("debug refresh ...")
                time.sleep(2)
                continue
            print(f"Processing Page {cur_page} / {num_of_pages}")
            num_rows = 0
            for prod in products:
                if prod["_type"] == "PRODUCT" and prod["adSource"] == None:
                    num_rows = num_rows + 1
                    percentage_sale = 0
                    if prod["pricing"]["was"] != 0:
                        percentage_sale = (prod["pricing"]["was"] - prod["pricing"]["now"]) / prod["pricing"]["was"]
                    new_row = {
                        "prodid": prod.get("id"),
                        "brand": prod.get("brand"),
                        "name": prod.get("name"),
                        "size": prod.get("size"),
                        "currentprice": prod.get("pricing", {}).get("now"),
                        "fullprice": prod.get("pricing", {}).get("was"),
                        "salespercentage": round(percentage_sale * 100, 2),
                        "rawdescription": prod.get("description")
                    }

                    self.total_product_df = pd.concat([self.total_product_df, pd.DataFrame([new_row])], ignore_index=True)
                    for heir in prod.get("onlineHeirs", []):
                        new_heir_row = {
                            "prodid": heir.get("id"),
                            "aisle": heir.get("aisle"),
                            "category": heir.get("category"),
                            "subcategory": heir.get("subCategory"),
                            "aisleid": heir.get("aisleId"),
                            "categoryid": heir.get("categoryId"),
                            "subcategoryid": heir.get("subCategoryId")
                        }
                        self.total_hier_df = pd.concat([self.total_hier_df, pd.DataFrame([new_row])], ignore_index=True)
                    with open("prod_save.pkl", "wb") as f:
                        pickle.dump(self, f)

            print(f"debug 3 {num_rows}")
            # try not to get banned
            time.sleep(10)
            # go next page / or loop
            cur_page = cur_page + 1
            if cur_page > num_of_pages:
                break

coles = Coles_Scrapper()
coles.scrape_all_categories()
for seo_code in coles.coles_categories:
    coles.scrape_inner_category(seo_code)
