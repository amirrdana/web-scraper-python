import os
import csv
import sys
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urljoin

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python main.py <website>")
    sys.exit(1)

# Is image extraction requested?
download_images = '-image' in sys.argv

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
    
# Function to extract domain name for output folder
def get_domain_name(url):
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "").replace(".", "_")

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

domain_name = get_domain_name(website)
# Create output directory for the specific website
output_dir = os.path.join("output", domain_name)
os.makedirs(output_dir, exist_ok=True)

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
            r.encoding = 'utf-8'
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
        r.encoding = 'utf-8'
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

# Write text data to CSV in the website's output directory
output_file = os.path.join(output_dir, 'output.csv')
try:
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(['Tag', 'Attributes', 'Text'])
        for tag_name, elements in data.items():
            for element in elements:
                writer.writerow([tag_name, element['attribute'], element['text']])
        print("Write to output successful")
except IOError as e:
    print(f"Error writing to file: {e}")

# Download images if -image flag is provided
if download_images:
    image_dir = os.path.join(output_dir, "images")
    os.makedirs(image_dir, exist_ok=True)
    img_tags = soup.find_all("img")
    downloaded = 0

    for i, img in enumerate(img_tags):
        img_url = img.get("src")
        if not img_url:
            continue  # Skip images without a valid source

        # Convert relative URLs to absolute URLs
        img_url = urljoin(website, img_url)

        try:
            img_data = requests.get(img_url, headers=additional_headers, timeout=10).content
            img_extension = os.path.splitext(img_url)[1].split("?")[0]  # Extract file extension
            if not img_extension:  # Default to .jpg if no extension is found
                img_extension = ".jpg"

            img_path = os.path.join(image_dir, f"image_{i+1}{img_extension}")
            with open(img_path, "wb") as img_file:
                img_file.write(img_data)
            downloaded += 1
            print(f"Downloaded: {img_path}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download image {img_url}: {e}")

    print(f"Downloaded {downloaded} images to {image_dir}")