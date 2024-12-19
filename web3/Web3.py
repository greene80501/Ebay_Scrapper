from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

# Function to scrape eBay data
def scrape_ebay_data(item):
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={item.replace(' ', '+')}&_sop=13&LH_Complete=1&LH_Sold=1"

    response = requests.get(search_url)
    if response.status_code != 200:
        return None, "Failed to fetch data from eBay."

    soup = BeautifulSoup(response.text, 'html.parser')

    excluded_keywords = ['broken', 'for parts', 'as is', 'Shop on eBay', 'parts only']

    items = []
    for listing in soup.select('.s-item'):
        try:
            title_tag = listing.select_one('.s-item__title')
            if not title_tag:
                continue
            title = title_tag.text

            if any(keyword.lower() in title.lower() for keyword in excluded_keywords):
                continue

            price_tag = listing.select_one('.s-item__price')
            if not price_tag:
                continue
            price_text = price_tag.text
            price = float(re.sub(r'[^\d.]', '', price_text))

            link_tag = listing.select_one('.s-item__link')
            link = link_tag['href'] if link_tag else "No link found"

            items.append({
                'title': title,
                'price': price,
                'link': link
            })
        except Exception:
            continue

    avg_price = round(sum(item['price'] for item in items) / len(items), 2) if items else 0

    return items, avg_price

# Function to check if an item is unrelated based on custom logic
def is_unrelated(item_title, keywords):
    """
    Determine if the item title is unrelated using a list of excluded keywords.
    """
    for keyword in keywords:
        if re.search(rf"\b{keyword}\b", item_title, re.IGNORECASE):
            return True
    return False

def process_results_file(file_name, excluded_keywords):
    """
    Read the file, filter unrelated items, and return them.
    """
    unrelated_items = []

    if not os.path.exists(file_name):
        return None, "The file does not exist. Please ensure the search was run first."

    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r"^\d+\.\s+(.*)$", line.strip())
            if match:
                item_title = match.group(1)
                if is_unrelated(item_title, excluded_keywords):
                    unrelated_items.append(item_title)

    return unrelated_items, None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    item = request.form['item']
    items, avg_price = scrape_ebay_data(item)

    if items is None:
        return render_template('index.html', error=avg_price)

    # Save item titles and indices to a text file
    file_name = f"{item.replace(' ', '_')}_results.txt"
    with open(file_name, "w", encoding="utf-8") as file:
        for index, entry in enumerate(items, start=1):
            file.write(f"{index}. {entry['title']}\n")

    return render_template('results.html', items=items, avg_price=avg_price, search_item=item)

@app.route('/ai-enhance', methods=['POST'])
def ai_enhance():
    import requests

    # Example: Fetch the data from a request
    data = request.get_json()
    search_item = data.get('search_item', '').replace(' ', '_')
    file_name = f"{search_item}_results.txt"
    upload_url = "http://127.0.0.1:1234/upload"

    # Step 1: Send the file to the server
    with open(file_name, 'rb') as file:
        files = {'file': file}
        response = requests.post(upload_url, files=files)

    if response.status_code == 200:
        print("File sent successfully!")
        print("Server's response:", response.text)  # Assuming the response is plain text
    else:
        print("Failed to send file. Status code:", response.status_code)

    # Step 2: Ask a question as plain text
    question_url = "http://localhost:1234/v1/chat/completions"  # Adjust if the endpoint is different
    question_text = "What is the purpose of this file?"  # Customize your question
    response = requests.post(question_url, data=question_text, headers={"Content-Type": "text/plain"})

    if response.status_code == 200:
        print("Server's answer:", response.text)  # Assuming the response is plain text
    else:
        print("Failed to ask the question. Status code:", response.status_code)


if __name__ == "__main__":
    app.run(debug=True)
