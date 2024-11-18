import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import sqlite3
from datetime import datetime

DB_FILE = "price_cache.db"

def connect_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            product_name TEXT,
            price REAL,
            date TEXT,
            image_url TEXT,
            product_url TEXT,
            site TEXT
        )
    ''')
    conn.commit()
    return conn

def save_data_to_db(product_name, data):
    conn = connect_db()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('DELETE FROM prices WHERE product_name = ? AND date = ?', (product_name, today))
    conn.commit()

    # Insert new data
    for item in data:
        cursor.execute('''
            INSERT INTO prices (product_name, price, date, image_url, product_url, site)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            item["name"], float(item["price"].replace("$", "")), today, item["image"], item["url"], item["site"]
        ))

    conn.commit()
    conn.close()

def load_data_from_db(product_name):
    conn = connect_db()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
        SELECT product_name, price, date, image_url, product_url, site
        FROM prices
        WHERE product_name = ? AND date = ?
    ''', (product_name, today))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "name": row[0],
            "price": f"${row[1]:.2f}",
            "date": row[2],
            "image": row[3],
            "url": row[4],
            "site": row[5]
        } for row in rows
    ]

def get_search_url(product_name):
    query = urllib.parse.quote_plus(product_name)
    return f"https://www.newegg.ca/p/pl?d={query}"

def get_info(product_name):
    prices = []
    url = get_search_url(product_name)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for product in soup.select(".item-container"):
        name = product.select_one(".item-title").text.strip()
        price = product.select_one(".price-current").text.strip()
        image = product.select_one(".item-img img")["src"]
        link = product.select_one(".item-title")["href"]
        clean_price = price.replace(",", "").replace("–", "").strip()
        
        prices.append({
            "site": "Newegg",
            "name": name,
            "price": clean_price,
            "image": image,
            "url": link
        })
    return prices

# def match_product_info(product_name):
#     data = get_info(product_name)
#     return [p for p in data if product_name.lower() in p["name"].lower()] # and all(keyword not in p["name"].lower() for keyword in ["laptop", "desktop"])

def match_product_info(product_name):
    data = get_info(product_name)
    product_parts = product_name.lower().split()  # Split product_name into parts

    return [
        p for p in data
        if all(part in p["name"].lower() for part in product_parts)
    ]


def sort_lowest_price(product_name):
    data = match_product_info(product_name)
    return sorted(data, key=lambda x: float(x["price"].replace("$", "")))

def get_cached_or_fresh_data(product_name):
    cached_data = load_data_from_db(product_name)
    if cached_data:
        return cached_data

    sorted_data = sort_lowest_price(product_name)
    save_data_to_db(product_name, sorted_data)
    return sorted_data

# data = match_product_info("32 GB RAM")
# print(data)