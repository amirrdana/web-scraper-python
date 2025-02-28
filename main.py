import csv
import sys
import random
import requests
from bs4 import BeautifulSoup

if len(sys.argv) != 2:
    print("Usage: python main.py <website>")
    sys.exit(1)

# Function to read headers from a file
def read_headers_from_file(file_path) -> list:
    try: 
        with open(file_path, 'r') as file:
            headers = [line.strip() for line in file if line.strip()]
        if not headers:
            print("Warning: user_agents.txt is empty. Proceeding without user agents")
        return headers
    except FileNotFoundError:
        print("User agent file not found. Proceeding without user agents")
        return []

website = sys.argv[1]
if "https://" not in website and "www." in website:
    website = f"https://{website}"
elif "https://" not in website and "www." not in website:
    website = f"https://www.{website}"
elif "https://" in website and "www." not in website:
    stop_point = 0
    trailer = ''
    for char in website:
        stop_point += 1
        if (char == '/' and trailer == '/'):
            break
        trailer = char
    website = "https://www." + website[stop_point:]

header_file = 'user_agents.txt'
header_list = read_headers_from_file(header_file)
random.shuffle(header_list)

# Additional headers to mimic a real browser
additional_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://www.google.com/',
}

# try to connect with user agent headers headers
success = False
if header_list:
    for index, header in enumerate(header_list, start=1):
        print(f"Trying header {index}...")
        headers = {'User-Agent': header}
        headers.update(additional_headers)
        try:
            r = requests.get(website, headers=headers, timeout=10)
            r.raise_for_status()
            success = True
            print(f"Connection to {website} successful with header {index}: {r.status_code}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Failed with header {index}, {e}")
if not success:
    print("Trying without user agent headers...")
    try:
        r = requests.get(website, headers=additional_headers, timeout=10)
        r.raise_for_status()
        print(f"Connection successful without user-agent: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection without user agents failed: {r.status_code}")
if not success:
    print(f"Connection failed")
    print("Exiting program")
    sys.exit()

html_content = r.text
soup = BeautifulSoup(html_content, 'html.parser')

data = dict()
for element in soup.find_all():
    tag_name = element.name
    if tag_name not in data:
        data[tag_name] = []
    element_data = {
        'attribute': str(element.attrs),
        'text': element.get_text(strip=True)
    }
    data[tag_name].append(element_data)

# print(data)

with open('output.csv', 'w', newline='', encoding='utf-8') as out:
    writer = csv.writer(out)
    writer.writerow(['Tag', 'Attributes', 'Text'])
    for tag_name, elements in data.items():
        for element in elements:
            writer.writerow([tag_name, element['attribute'], element['text']])
    print("Write to output successful")