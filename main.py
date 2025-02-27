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
data['links'] = [link.get('href') for link in soup.find_all('a') if link.get('href')]
data['images'] = [img.get('src') for img in soup.find_all('img') if img.get('src')]

# print(data)

with open('output.csv', 'w') as out:
    writer = csv.writer(out)
    writer.writerow(['Links', 'Images'])
    for link, image in zip_longest(data['links'], data['images'], fillvalue=''):
        writer.writerow([link, image])