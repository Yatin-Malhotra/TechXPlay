# from statsmodels.tsa.arima.model import ARIMA
# import pandas as pd
# import sqlite3
# import pandas as pd
# from datetime import datetime, timedelta

# DB_FILE = 'price_data.db'

# def check_historical_data(product_name):
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()

#     query = """
#     SELECT COUNT(DISTINCT date) FROM prices
#     WHERE product_name = ?
#     """
#     cursor.execute(query, (f"%{product_name}%",))
#     count = cursor.fetchone()[0]

#     conn.close()
#     return count

# def load_price_data(product_name):
#     conn = sqlite3.connect(DB_FILE)
#     query = """
#     SELECT date, price FROM prices
#     WHERE product_name = ?
#     ORDER BY date
#     """
#     df = pd.read_sql_query(query, conn, params=(f"%{product_name}%",))
#     conn.close()
#     df['date'] = pd.to_datetime(df['date'])
#     df.set_index('date', inplace=True)
#     df['price'] = df['price'].astype(float)  # Ensure prices are floats
#     return df

# def forecast_price(product_name, days_ahead):
#     df = load_price_data(product_name)

#     # Fit ARIMA model
#     model = ARIMA(df['price'], order=(5, 1, 0))  # You may need to tune the order
#     model_fit = model.fit()

#     # Forecast
#     forecast = model_fit.forecast(steps=days_ahead)

#     # Create a DataFrame for the forecast with dates
#     start_date = df.index[-1] + timedelta(days=1)
#     forecast_dates = [start_date + timedelta(days=i) for i in range(days_ahead)]
#     forecast_df = pd.DataFrame({'date': forecast_dates, 'price': forecast})

#     # Find the minimum predicted price
#     min_price_row = forecast_df.loc[forecast_df['price'].idxmin()]
#     return min_price_row['date'], min_price_row['price']

# # # Example usage:
# # product_name = "MSI Ventus GeForce RTX 4060 Video Card RTX 4060 VENTUS 2X WHITE 8G OC"
# # count = check_historical_data(product_name)
# # print("Count:", count)

# # if count > 360:
# #     days_ahead = 30  # Predict for the next 30 days
# #     prediction = forecast_price(product_name, days_ahead)
# #     print("Price prediction for the next 30 days:")
# #     print(prediction)
# # else:
# #     print("Not enough data available. Please gather more historical data.")

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np

DB_FILE = 'price_data.db'

def check_historical_data(product_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = """
    SELECT COUNT(DISTINCT date) FROM prices
    WHERE product_name LIKE ?
    """
    cursor.execute(query, (f"%{product_name}%",))
    count = cursor.fetchone()[0]

    conn.close()
    return count

def load_price_data(product_name):
    conn = sqlite3.connect(DB_FILE)
    query = """
    SELECT date, price FROM prices
    WHERE product_name LIKE ?
    ORDER BY date
    """
    df = pd.read_sql_query(query, conn, params=(f"%{product_name}%",))
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df['price'] = df['price'].astype(float)  # Ensure prices are floats
    return df

def forecast_price(product_name, days_ahead):
    df = load_price_data(product_name)

    # Prepare data for Linear Regression
    df['days_since_start'] = (df.index - df.index[0]).days
    X = df['days_since_start'].values.reshape(-1, 1)  # Independent variable
    y = df['price'].values  # Dependent variable

    # Train Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Forecast future prices
    last_day = df['days_since_start'].iloc[-1]
    future_days = np.arange(last_day + 1, last_day + days_ahead + 1).reshape(-1, 1)
    predicted_prices = model.predict(future_days)

    # Create a DataFrame for the forecast with dates
    start_date = df.index[-1] + timedelta(days=1)
    forecast_dates = [start_date + timedelta(days=i) for i in range(days_ahead)]
    forecast_df = pd.DataFrame({'date': forecast_dates, 'price': predicted_prices})

    # Find the minimum predicted price
    min_price_row = forecast_df.loc[forecast_df['price'].idxmin()]
    return min_price_row['date'], min_price_row['price']
