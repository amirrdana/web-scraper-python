import csv
import sys
import requests
from bs4 import BeautifulSoup
from itertools import zip_longest

if len(sys.argv) != 2:
    print("Usage: python main.py <website>")
    sys.exit(1)

website = sys.argv[1]
if "https://" not in website and "www." in website:
    website = f"https://{website}"
elif "https://" not in website and "www." not in website:
    website = f"https://www.{website}"
elif "https://" in website and "www." not in website:
    pass
    # implement

try :
    r = requests.get(website)
    r.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error fetching the webpage {website}: {e}")
    sys.exit(1)
print(f"Connection to {website} successful: {r.status_code}")
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