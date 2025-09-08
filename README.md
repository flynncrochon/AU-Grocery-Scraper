# Grocery Price Scraper & Comparator

A Python-based project to scrape grocery data from major Australian retailers (Coles and Woolworths) and compare prices. This tool allows users to track product prices, analyze trends, and make informed shopping decisions.

---

## Features

- Scrape product information including:
  - Name
  - Brand
  - Price
  - Unit size / weight
  - Category
- Pull data from multiple stores:
  - Coles
  - Woolworths
- Compare prices between stores for the same products.
- Export data to `.csv` or `.dat` for further analysis.
- Modular design: Add more retailers or custom scraping logic easily.

## Storage Structure

Scraped data is stored in a structured folder system for easy tracking and weekly comparisons:
```
Coles/
└── 04-09-2025/ # Week-ending date (last Wednesday)
└── pantry/ # Category (e.g., pantry, dairy, frozen)
├── 1_product.csv # Product details for page 1
├── 1_hier.csv # Hierarchy mapping for page 1
├── 2_product.csv
├── 2_hier.csv
└── ...
```
### Folder Breakdown

- **Week-ending date folder**  
  Each run is stored under the most recent Wednesday (e.g., `04-09-2025`).  
  This provides a weekly snapshot of product data.

- **Category folder**  
  Inside each week’s folder, products are grouped by category (e.g., `pantry`, `dairy`, `frozen`).  
  Categories mirror the retailer’s site structure.

- **Page files**  
  Categories are split into pages, and each page generates two CSV files:
  - `X_product.csv` → product-level details  
    Columns:  
    - `prodid`  
    - `brand`  
    - `name`  
    - `size`  
    - `current_price`  
    - `full_price`  
    - `raw_description`
  - `X_hier.csv` → product hierarchy (aisle/category placement)  
    Columns:  
    - `prodid`  
    - `aisle`  
    - `category`  
    - `subcategory`  
    - `aisle_id`  
    - `category_id`  
    - `subcategory_id`

- **Incremental scraping**  
  If a page file already exists (e.g., `2_product.csv`), the scraper will skip re-downloading it.  
  This makes scraping resumable if interrupted.
---
