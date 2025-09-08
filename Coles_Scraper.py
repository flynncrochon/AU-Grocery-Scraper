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
        print("\n ============================== Initialising Coles Session ... ============================== ")

        week = get_previous_wednesday()
        self.__current_we = week
        print(f"Doing week: {week}")

        os.makedirs(self.__csv_dump_loc + week, exist_ok=True)
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
        print(f"Found categories {return_cat}")
        self.coles_seo_codes = return_cat

    def scrape_all_inner_categories(self):
        current = 1
        for seo_code in self.coles_seo_codes:
            if seo_code != "pantry":
                continue
            print(f"\n ==================== Processing Category: {seo_code} [{current} / {len(self.coles_seo_codes)}]====================")
            self.scrape_inner_category(seo_code)
            current = current + 1

    def scrape_inner_category(self, seo_code):
        cur_page = 1
        num_of_pages = 1
        while cur_page <= num_of_pages:
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
            json_search_results = json_data["pageProps"]["searchResults"]
            products = json_search_results["results"]
            page_size = json_search_results["pageSize"]
            if json_search_results["pageSize"] == 0:
                print(f">> Reached the end [{seo_code}] <<")
                break
            # update number of pages
            num_of_pages = json_search_results["noOfResults"] / page_size
            num_of_pages = math.ceil(num_of_pages)
            if page_size != 48:
                print(f"Incorrect page_size: [{page_size}]")
                time.sleep(10)
                continue

            product_rows = []
            hier_rows    = []

            product_col = ["prodid", "brand", "name", "size", "current_price", "full_price","raw_description"]
            hier_col    = ["prodid", "aisle", "category", "subcategory", "aisle_id", "category_id", "subcategory_id"]

            num_rows = 0
            for prod in products:
                # if these are not products or ads we just skip for now
                if prod["_type"] != "PRODUCT" or prod["adSource"]:
                    continue
                num_rows += 1
                current_price = None
                full_price = None
                pricing = prod.get("pricing")
                if pricing:
                    current_price = pricing.get("now")
                    full_price = pricing.get("was")

                prod_row = {
                    product_col[0]: prod.get("id"),
                    product_col[1]: prod.get("brand"),
                    product_col[2]: prod.get("name"),
                    product_col[3]: prod.get("size"),
                    product_col[4]: current_price,
                    product_col[5]: full_price,
                    product_col[6]: prod.get("description")
                }
                product_rows.append(prod_row)

                for heir in prod.get("onlineHeirs", []):
                    heir_row = {
                        hier_col[0]: prod.get("id"),
                        hier_col[1]: heir.get("aisle"),
                        hier_col[2]: heir.get("category"),
                        hier_col[3]: heir.get("subCategory"),
                        hier_col[4]: heir.get("aisleId"),
                        hier_col[5]: heir.get("categoryId"),
                        hier_col[6]: heir.get("subCategoryId")
                    }
                    hier_rows.append(heir_row)

            product_df = pd.DataFrame(product_rows, columns=product_col)
            hier_df    = pd.DataFrame(hier_rows   , columns=hier_col)

            product_df.to_csv(write_csv_path + f"/{cur_page}_product.csv", mode='w', header=True, index=False)
            hier_df.to_csv   (write_csv_path + f"/{cur_page}_hier.csv"   , mode='w', header=True, index=False)

            print(f">> Processed Page {cur_page} / {num_of_pages} [✔] >> [{num_rows}] products validated")

            # try not to get banned
            time.sleep(10)
            # go next page / or loop
            cur_page += 1