from operator import truediv

import pickle
#import json
import pandas as pd
import math
import json
import time
import random
from Get_HTML import Get_HTML

class Coles_Scraper:

    coles_seo_codes = []
    total_product_df = pd.DataFrame(
        columns=["prodid", "brand", "name", "size", "currentprice", "fullprice", "salespercentage", "rawdescription"])
    total_hier_df = pd.DataFrame(
        columns=["prodid", "aisle", "category", "subcategory", "aisleid", "categoryid", "subcategoryid"])
    __build_id = "0"

    def __init__(self, ssid):
        print(" ============================== Initialising Coles Session ... ============================== ")
        self.getter = Get_HTML(
            ssid,
            "As you were browsing something about your browser made us think you were a bot"
        )
        print("Attempting html query")
        soup = self.getter.get("https://www.coles.com.au/browse")

        next_data = soup.find('script', id='__NEXT_DATA__')
        json_data = json.loads(next_data.string)

        self.__build_id = json_data["buildId"]
        print(f"Coles Build ID: {self.__build_id}")

        categories = json_data["props"]["pageProps"]["allProductCategories"]["catalogGroupView"]
        return_cat = []
        for cat in categories:
            return_cat.append(cat["seoToken"])
            #print(cat["id"], " - ", cat["seoToken"])
        print(f"Found categories {return_cat}")
        self.coles_seo_codes = return_cat

    def scrape_all_inner_categories(self):
        current = 1
        for seo_code in self.coles_seo_codes:
            print(f" ==================== Processing Category: {seo_code} [{current} / {len(self.coles_seo_codes)}]====================")
            self.scrape_inner_category(seo_code)
            current = current + 1

    def scrape_inner_category(self, seo_code):
        cur_page = 1
        while True:

            print(f"https://www.coles.com.au/browse/{seo_code}?page={cur_page}")
            # this below link is weird
            #print(f"https://www.coles.com.au/_next/data/{self.build_id}/en/browse/{seo_code}.json?slug={seo_code}?page={cur_page}")

            time.sleep(2)
            soup = self.getter.get(f"https://www.coles.com.au/browse/{seo_code}?page={cur_page}")
            # Find the script tag with id="__NEXT_DATA__"
            next_data = soup.find('script', id='__NEXT_DATA__')
            json_data = json.loads(next_data.string)

            products = json_data["props"]["pageProps"]["searchResults"]["results"]

            num_of_pages = json_data["props"]["pageProps"]["searchResults"]["noOfResults"] / json_data["props"]["pageProps"]["searchResults"]["pageSize"]
            num_of_pages = math.ceil(num_of_pages)
            if json_data["props"]["pageProps"]["searchResults"]["pageSize"] < 48:
                #print("debug refresh ...")
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