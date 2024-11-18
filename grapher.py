import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_FILE = 'price_data.db'

def load_price_data(product_name):
    conn = sqlite3.connect(DB_FILE)
    query = """
    SELECT date, price FROM prices
    WHERE product_name LIKE ?
    ORDER BY date
    """
    # Include wildcards for LIKE
    df = pd.read_sql_query(query, conn, params=(f"%{product_name}%",))
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

def save_price_history_graph(product_name):
    df = load_price_data(product_name)

    if df.empty:
        print(f"No price data found for {product_name}")
        return

    # Create the graph
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['price'], label=product_name, color='b')
    plt.title(f"Price History for {product_name}")
    plt.xlabel("Date")
    plt.ylabel("Price (CAD)")
    plt.legend()
    plt.grid()

    # Save graph to static folder
    graph_path = f'static/graphs/{product_name}.png'
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    plt.savefig(graph_path)
    plt.close()
    print(f"Graph saved to {graph_path}")

# Generate the graph for a specific product
#save_price_history_graph("GIGABYTE GeForce RTX 4060 EAGLE OC 8G Graphics Card, 3x WINDFORCE Fans, 8GB 128-bit GDDR6, GV-N4060EAGLE OC-8GD Video Card")
