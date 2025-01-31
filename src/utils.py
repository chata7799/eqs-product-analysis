import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
BESTBUY_API_KEY = os.getenv("BESTBUY_API_KEY")

def clean_price(price_value):
    if pd.isnull(price_value):
        return None
    price_str = str(price_value).replace('$', '').strip()
    try:
        return float(price_str)
    except ValueError:
        return None

def clean_category(category_value):
    if pd.isnull(category_value):
        return None
    return str(category_value).strip().capitalize()

def clean_stock(stock_value):
    if pd.isnull(stock_value):
        return None
    stock_str = str(stock_value).lower().strip()
    if stock_str == 'out of stock':
        return 0
    try:
        return int(stock_str)
    except ValueError:
        return None

def fetch_external_data_bestbuy(keyword):
    """
    Calls the Best Buy Products API to get an approximate average 'salePrice'
    for items matching the given keyword.
    """
    if not BESTBUY_API_KEY:
        return 10.0

    base_url = "https://api.bestbuy.com/v1/products"
    query = f"(search={keyword})"
    params = {
        "format": "json",
        "apiKey": BESTBUY_API_KEY
    }
    url = f"{base_url}(({query}))"

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            if not products:
                return 10.0

            prices = [p.get("salePrice") for p in products if p.get("salePrice") is not None]
            if prices:
                return sum(prices) / len(prices)
            else:
                return 10.0
        else:
            return 10.0
    except requests.exceptions.RequestException:
        return 10.0
