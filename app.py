from flask import Flask, render_template, request, jsonify
import sqlite3
import subprocess
from scraper_electronics import get_cached_or_fresh_data
from grapher import save_price_history_graph
from sync import sync_databases
from prediction import check_historical_data, forecast_price

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    # Get data either from cache or scrape Newegg
    products = get_cached_or_fresh_data(query)
    sync_databases()
    return jsonify(products)

@app.route('/product/<product_name>')
def product_detail(product_name):
    # Fetch data for the specific product
    conn = sqlite3.connect('price_cache.db')
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, price, date, image_url, product_url, site FROM prices WHERE product_name=?", (product_name,))
    product_data = cursor.fetchall()
    conn.close()

    # Generate the price history graph
    # save_price_history_graph(product_name)  # Generate and save the graph as static/graphs/<product_name>_price_history.png

    # Check if product data was found
    if product_data:
        # Use the first entry in `product_data` as an example, assuming all entries are identical for `product_name`
        product = {
            "name": product_data[0][0],
            "price": product_data[0][1],
            "date": product_data[0][2],
            "image": product_data[0][3],
            "url": product_data[0][4],
            "site": product_data[0][5]
        }

        min_date, min_price = None, None
        count = check_historical_data(product_name)
        min_date, min_price = forecast_price(product_name, 30)
    else:
        # Handle the case where no product data is found
        product = None

    return render_template(
        'product_detail.html',
        product=product,
        product_name=product_name,
        graph_url=f'/static/graphs/{product_name}_price_history.png',
        min_date=min_date.strftime('%Y-%m-%d') if min_date else None,
        min_price=min_price
    )

if __name__ == '__main__':
    app.run(debug=True)
