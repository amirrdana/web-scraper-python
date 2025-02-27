import csv
import requests
from bs4 import BeautifulSoup
from itertools import zip_longest

r = requests.get("https://www.google.com")
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

# for link in links:
#     print(link.get('href'))
# for image in imgs:
#     print(image.get('src'))