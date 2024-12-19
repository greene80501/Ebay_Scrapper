import requests
from bs4 import BeautifulSoup
import re

def scrape_ebay_data(item, output_file):
    # Search URL for eBay sold items
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={item.replace(' ', '+')}&_sop=13&LH_Complete=1&LH_Sold=1"

    # Fetch and parse the page
    response = requests.get(search_url)
    if response.status_code != 200:
        print("Failed to fetch data from eBay. Please check the URL or your internet connection.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Keywords to exclude
    excluded_keywords = ['broken', 'for parts', 'as is', 'Shop on eBay', 'parts only']

    # Extract item data
    items = []
    for listing in soup.select('.s-item'):
        try:
            # Extracting title
            title_tag = listing.select_one('.s-item__title')
            if not title_tag:
                continue
            title = title_tag.text

            # Check for excluded keywords in the title
            if any(keyword.lower() in title.lower() for keyword in excluded_keywords):
                continue

            # Extracting price
            price_tag = listing.select_one('.s-item__price')
            if not price_tag:
                continue
            price_text = price_tag.text
            price = float(re.sub(r'[^\d.]', '', price_text))

            # Extracting date sold
            date_tag = listing.select_one('.s-item__title--tagblock span.POSITIVE')
            date_sold = date_tag.text if date_tag else "No date found"

            # Extracting link
            link_tag = listing.select_one('.s-item__link')
            link = link_tag['href'] if link_tag else "No link found"

            items.append({
                'title': title,
                'price': price,
                'date_sold': date_sold,
                'link': link
            })
        except Exception as e:
            # Skip items with missing data
            continue

    # Calculate the average price
    if items:
        avg_price = round(sum(item['price'] for item in items) / len(items), 2)
    else:
        avg_price = 0

    # Save titles to a text file and print all item data
    with open(output_file, 'w', encoding='utf-8') as file:
        print(f"\nResults for '{item}':")
        for i, item in enumerate(items, start=1):
            # Print each item's details
            print(f"{i}. {item['title']} - ${item['price']} - {item['date_sold']}")
            print(f"   Link: {item['link']}")
            
            # Write index and title to file
            file.write(f"{i}. {item['title']}\n")

    # Print the average price
    print(f"The Avg Price was: {avg_price}")
    print(f"Saved {len(items)} titles to {output_file}")

# Example usage
search_item = input("Enter the item to search on eBay: ")
output_filename = f"{search_item.replace(' ', '_')}_data.txt"
scrape_ebay_data(search_item, output_filename)
