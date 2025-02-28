import csv
import sys
import requests
from bs4 import BeautifulSoup

if len(sys.argv) != 2:
    print("Usage: python main.py <website>")
    sys.exit(1)

# Function to read headers from a file
def read_headers_from_file(file_path):
    with open(file_path, 'r') as file:
        headers = [line.strip() for line in file if line.strip()]
    return headers

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

# try to connect with user agent headers headers
success = False
for index, header in enumerate(header_list, start=1):
    print(f"Trying header {index}...")
    headers = {'User-Agent': header}
    try:
        r = requests.get(website, headers=headers)
        r.raise_for_status
        if (r.status_code == 200):
            success = True
            print(f"Connection to {website} successful with header {index}: {r.status_code}")
            break
    except requests.exceptions.RequestException as e:
        print(f"Failed with header {index}, {e}")
if not success:
    print(f"Connection failed with status code: {r.status_code}")
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
        'attribute': element.attrs,
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