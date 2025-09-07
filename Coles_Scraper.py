import pickle
#import json
import pandas as pd
import math
import json
import time
import os

from Web_Getter import Web_Getter
from datetime import datetime, timedelta


def get_previous_wednesday():
    # Current date
    today = datetime.today()
    # ISO weekday: Monday=1, Sunday=7
    weekday = today.isoweekday()
    # Days since last Wednesday (Wednesday=3)
    days_since_wednesday = (weekday - 3) % 7
    last_wednesday = today - timedelta(days=days_since_wednesday)
    au_date = last_wednesday.strftime("%d-%m-%Y")

    return au_date

class Coles_Scraper:

    coles_seo_codes = []
    __build_id = "0"
    __coles_status_csv = "Coles/coles_status.csv"
    __csv_dump_loc = "Coles/"
    __status = pd.DataFrame()
    __current_we = ""

    def __init__(self, ssid):
        print(" ============================== Initialising Coles Session ... ============================== ")

        week = get_previous_wednesday()
        os.makedirs(self.__csv_dump_loc + week, exist_ok=True)

        self.__current_we = week

        print(f"Doing week: {week}")

        self.getter = Web_Getter(
            ssid,
            "As you were browsing something about your browser made us think you were a bot"
        )

        soup = self.getter.get_html("https://www.coles.com.au/browse")

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
            if seo_code != "pantry":
                continue
            print(f" ==================== Processing Category: {seo_code} [{current} / {len(self.coles_seo_codes)}]====================")
            self.scrape_inner_category(seo_code)
            current = current + 1

    def scrape_inner_category(self, seo_code):
        cur_page = 1
        while True:
            write_csv_path = f"{self.__csv_dump_loc}/{self.__current_we}/{seo_code}"

            if (os.path.exists(write_csv_path + f"/{cur_page}_product.csv") or
                os.path.exists(write_csv_path + f"/{cur_page}_hier.csv")):
                print(f">> Skipping page {cur_page}")
                cur_page = cur_page + 1
                continue

            os.makedirs(write_csv_path, exist_ok=True)
            time.sleep(2)
            json_data = self.getter.get_json_api(f"https://www.coles.com.au/_next/data/{self.__build_id}/en/browse/{seo_code}.json?slug={seo_code}&page={cur_page}",
                                                 f"https://www.coles.com.au/browse/{seo_code}?page={cur_page-1}"
                                                 )
            products = json_data["pageProps"]["searchResults"]["results"]
            page_size = json_data["pageProps"]["searchResults"]["pageSize"]
            if json_data["pageProps"]["searchResults"]["pageSize"] == 0:
                print("Reached the end?")
                break

            num_of_pages = json_data["pageProps"]["searchResults"]["noOfResults"] / page_size
            num_of_pages = math.ceil(num_of_pages)
            #print(f"debug {json_data["pageProps"]["searchResults"]["noOfResults"]} || {page_size} || {num_of_pages}")
            if page_size != 48:
                print(f"Incorrect page_size: [{page_size}]")
                time.sleep(10)
                continue

            product_rows = []
            hier_rows = []

            num_rows = 0
            for prod in products:
                # if these are not products or ads we just skip for now
                if prod["_type"] != "PRODUCT" or prod["adSource"] is not None:
                    continue
                num_rows = num_rows + 1
                current_price = None
                full_price = None
                sale_percentage = None
                pricing = prod.get("pricing")
                if pricing:
                    current_price = pricing.get("now")
                    full_price = pricing.get("was")
                    percentage_sale = 0
                    if pricing.get("was") != 0:
                        percentage_sale = (pricing.get("was") - pricing.get("now")) / pricing.get("was")
                    sale_percentage =  round(percentage_sale * 100, 2)

                new_row = {
                    "prodid": prod.get("id"),
                    "brand": prod.get("brand"),
                    "name": prod.get("name"),
                    "size": prod.get("size"),
                    "currentprice": current_price,
                    "fullprice": full_price,
                    "salespercentage": sale_percentage,
                    "rawdescription": prod.get("description")
                }
                product_rows.append(new_row)

                for heir in prod.get("onlineHeirs", []):
                    new_heir_row = {
                        "prodid": prod.get("id"),
                        "aisle": heir.get("aisle"),
                        "category": heir.get("category"),
                        "subcategory": heir.get("subCategory"),
                        "aisleid": heir.get("aisleId"),
                        "categoryid": heir.get("categoryId"),
                        "subcategoryid": heir.get("subCategoryId")
                    }
                    hier_rows.append(new_heir_row)

            product_col = ["prodid", "brand", "name", "size", "currentprice", "fullprice", "salespercentage","rawdescription"]
            hier_col = ["prodid", "aisle", "category", "subcategory", "aisleid", "categoryid", "subcategoryid"]

            product_df = pd.DataFrame(product_rows, columns=product_col)
            hier_df = pd.DataFrame(hier_rows, columns=hier_col)

            product_df.to_csv(write_csv_path + f"/{cur_page}_product.csv", mode='w', header=True, index=False)
            hier_df.to_csv   (write_csv_path + f"/{cur_page}_hier.csv"   , mode='w', header=True, index=False)

            print(f">> Processed Page {cur_page} / {num_of_pages} [✔] >> [{num_rows}] products validated")

            # try not to get banned
            time.sleep(10)
            # go next page / or loop
            cur_page = cur_page + 1
            if cur_page > num_of_pages:
                break