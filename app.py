import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

url = "https://www.jumia.co.ke/computing/"
headers = {'User-Agent': 'Mozilla/5.0'}
products = []

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
product_cards = soup.find_all('article', class_='prd')[:10]

for product in product_cards:
    title = "Unknown"
    price = 0
    
    # Try multiple title tags
    title_tag = (product.find('h3', class_='name') or
                 product.find('div', class_='name') or
                 product.find('a', class_='core'))
    if title_tag:
        title = title_tag.get_text(strip=True)
    
    price_tag = product.find('div', class_='prc')
    if price_tag:
        price_text = price_tag.get_text(strip=True)
        cleaned_price = price_text.replace('KSh', '').replace(',', '').strip()
        if cleaned_price.replace('.', '').isdigit():
            price = float(cleaned_price)
    
    products.append({'title': title, 'price_kes': price})

if len(products) > 0:
    api_key = "f9eff7ba103130f95bf2b710"
    api_url = f"https://api.exchangerate-api.com/v4/latest/KES?access_key={api_key}"
    exchange_response = requests.get(api_url)
    exchange_data = exchange_response.json()
    if 'rates' in exchange_data:
        rate = exchange_data['rates']['USD']
        for product in products:
            product['price_usd'] = round(product['price_kes'] * rate, 2)

if len(products) > 0:
    filename = f"jumia_prices_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'price_kes', 'price_usd'])
        writer.writeheader()
        writer.writerows(products)

for product in products:
    print(f"{product['title']}")
    print(f"KSh {product['price_kes']} (KES)")
    if 'price_usd' in product:
        print(f"${product['price_usd']} (USD)")