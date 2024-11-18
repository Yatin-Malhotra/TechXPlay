import sqlite3

# Database file paths
CACHE_DB = 'price_cache.db'
HISTORICAL_DB = 'price_data.db'

# Function to update historical database with new data from cache
def sync_databases():
    # Connect to both databases
    cache_conn = sqlite3.connect(CACHE_DB)
    hist_conn = sqlite3.connect(HISTORICAL_DB)
    cache_cursor = cache_conn.cursor()
    hist_cursor = hist_conn.cursor()
    
    # Ensure tables exist in both databases
    hist_cursor.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        date TEXT,
        price REAL,
        image_url TEXT,
        product_url TEXT,
        UNIQUE(product_name, date)  -- Ensure no duplicates per product/date
    )
    """)
    hist_conn.commit()
    
    # Fetch all records from cache
    cache_cursor.execute("SELECT product_name, date, price, image_url, product_url FROM prices")
    cache_data = cache_cursor.fetchall()
    
    # Insert or update records in historical database
    for product_name, date, price, image_url, product_url in cache_data:
        # Insert or replace (update if exists) the record in the historical DB
        hist_cursor.execute("""
        INSERT OR REPLACE INTO prices (product_name, date, price, image_url, product_url)
        VALUES (?, ?, ?, ?, ?)
        """, (product_name, date, price, image_url, product_url))
    
    # Commit changes and close connections
    hist_conn.commit()
    cache_conn.close()
    hist_conn.close()
    print("Data synced successfully from price_cache.db to price_data.db.")

# Run the sync function
# sync_databases()
