import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

# Function to get Gold Prices in Pakistan
def get_pakistan_gold_prices():
    url = 'https://gold.pk/pakistan-gold-rates-xaup.php'
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code != 200:
        print("Failed to retrieve gold prices.")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    gold_price_elements = soup.find_all('p', class_='goldratehome')

    gold_prices = {}
    
    for price_element in gold_price_elements:
        price = price_element.text.strip()
        gold_type_element = price_element.find_next_sibling('p')  # Check the next <p> tag
        
        if gold_type_element:
            gold_type = gold_type_element.text.strip()
            gold_prices[gold_type] = price  # Store in dictionary

    return gold_prices

# Function to scrape USD to PKR exchange rate
def get_usd_to_pkr():
    url = "https://www.x-rates.com/table/?from=USD&amount=1"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code != 200:
        print("Failed to retrieve exchange rate data.")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all("table")

    if not tables:
        print("No exchange rate tables found.")
        return None

    # Iterate through tables to find PKR exchange rate
    for table in tables:
        for row in table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) > 1 and "Pakistani Rupee" in columns[0].text:
                exchange_rate = columns[1].text.strip()
                return exchange_rate

    print("Exchange rate for PKR not found.")
    return None

# Function to get Pakistan's inflation rate from World Bank API
def get_pakistan_inflation_wb():
    url = "http://api.worldbank.org/v2/country/PK/indicator/FP.CPI.TOTL.ZG?format=json"
    
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve inflation data.")
        return None

    try:
        data = response.json()
        if data and len(data) > 1 and isinstance(data[1], list):
            latest_data = max(data[1], key=lambda x: x['date'])  # Get latest year
            return latest_data['value']
    except (KeyError, IndexError, ValueError):
        print("Error parsing inflation data.")

    return None

# Function to save all economic data to a CSV file
def save_economic_data():
    today_date = datetime.now().strftime("%Y-%m-%d")
    csv_file = "data.csv"

    # Fetch data
    gold_prices = get_pakistan_gold_prices()
    usd_to_pkr = get_usd_to_pkr()
    inflation_rate = get_pakistan_inflation_wb()

    # Define headers
    csv_headers = ["Date", "Type", "Category", "Value"]

    # Check if file exists
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write headers if file is empty
        if not file_exists:
            writer.writerow(csv_headers)

        # Write USD to PKR exchange rate
        if usd_to_pkr:
            writer.writerow([today_date, "Exchange Rate", "USD to PKR", usd_to_pkr])

        # Write Inflation Rate
        if inflation_rate:
            writer.writerow([today_date, "Inflation", "CPI Inflation", inflation_rate])

        # Write Gold Prices
        for gold_type, price in gold_prices.items():
            writer.writerow([today_date, "Gold", gold_type, price])

    print("All economic data saved successfully!")

    # # Commit and push the updated CSV file to GitHub
    # os.system("git config --local user.email 'github-actions@github.com'")
    # os.system("git config --local user.name 'GitHub Actions'")
    # os.system("git add data.csv")
    # os.system('git commit -m "Updated economic data: {}"'.format(today_date))
    # os.system("git push")

# Run the function
save_economic_data()
