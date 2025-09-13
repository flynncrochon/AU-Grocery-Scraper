import sqlite3
import pandas as pd
import os

db_path = 'coles.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_details (
        prodid INTEGER PRIMARY KEY,
        brand TEXT,
        name TEXT,
        size TEXT,
        current_price REAL,
        full_price REAL,
        raw_description TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_categories (
        prodid INTEGER,
        aisle TEXT,
        category TEXT,
        subcategory TEXT,
        aisle_id INTEGER,
        category_id INTEGER,
        subcategory_id INTEGER,
        FOREIGN KEY (prodid) REFERENCES product_details (prodid)
    )
''')

def load_csv_to_table(csv_path, table_name, cursor, conn):
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return
    
    df = pd.read_csv(csv_path)
    
    if table_name == 'product_details':
        expected_columns = ['prodid', 'brand', 'name', 'size', 'current_price', 'full_price', 'raw_description']
        if not all(col in df.columns for col in expected_columns):
            print(f"Error: {csv_path} does not contain all required columns for {table_name}.")
            return
        
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR IGNORE INTO product_details (prodid, brand, name, size, current_price, full_price, raw_description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['prodid'], row['brand'], row['name'], row['size'], row['current_price'], row['full_price'], row['raw_description']))
    
    elif table_name == 'product_categories':
        expected_columns = ['prodid', 'aisle', 'category', 'subcategory', 'aisle_id', 'category_id', 'subcategory_id']
        if not all(col in df.columns for col in expected_columns):
            print(f"Error: {csv_path} does not contain all required columns for {table_name}.")
            return
        
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR IGNORE INTO product_categories (prodid, aisle, category, subcategory, aisle_id, category_id, subcategory_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['prodid'], row['aisle'], row['category'], row['subcategory'], row['aisle_id'], row['category_id'], row['subcategory_id']))
    
    conn.commit()
    print(f"Data from {csv_path} inserted into {table_name} successfully.")

categories = [
    'baby', 'bakery', 'chips-chocolates-snacks', 'dairy-eggs-fridge', 'deli',
    'dietary-world-foods', 'down-down', 'drinks', 'frozen', 'fruit-vegetables',
    'health-beauty', 'household', 'liquorland', 'meat-seafood', 'pantry', 'pet'
]

category = 'baby'
base_path = f'./Coles/10-09-2025/{category}/'
file_number = 1

product_csv = f'{base_path}{file_number}_product.csv'
hier_csv = f'{base_path}{file_number}_hier.csv' 

load_csv_to_table(product_csv, 'product_details', cursor, conn)
load_csv_to_table(hier_csv, 'product_categories', cursor, conn)

for file_number in range(2, 10): 
    product_csv = f'{base_path}{file_number}_product.csv'
    hier_csv = f'{base_path}{file_number}_hier.csv' 
    if os.path.exists(product_csv) and os.path.exists(hier_csv):
        load_csv_to_table(product_csv, 'product_details', cursor, conn)
        load_csv_to_table(hier_csv, 'product_categories', cursor, conn)
    else:
        break

conn.close()
print("Database processing completed.")