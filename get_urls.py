import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
import json

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def get_all_urls(base_url, endpoint, letter, search_endpoint):
    # Send a GET request to the specified endpoint
    params = {'letter': letter}
    url = urljoin(base_url, endpoint) + '?' + urlencode(params)

    print(" ")
    print("URL: ", url)
    print("SEARCH ENDPOINT: ", search_endpoint)

    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all anchor tags (<a>) with href attribute
        links = soup.find_all('a', href=True)

        # Extract and print URLs that start with www.mywebsite/events/
        valid_urls = []
        for link in links:
            if (link['href'].startswith(search_endpoint) and
                    'index' not in link['href']):
                valid_urls.append(link['href'])

        return valid_urls
    else:
        print(
            f"Error: Unable to fetch content from {urljoin(base_url, endpoint)}")
        return []


# Replace 'www.mywebsite.com' and '/events/' with your actual website and endpoint
BASE_URL = 'https://www.mayoclinic.org'
# endpoint = '/diseases-conditions/index'
# search_endpoint = 'https://www.mayoclinic.org/diseases-conditions/'

resources = {
    'diseases': {
        'endpoint': '/diseases-conditions/index',
        'search_endpoint': 'https://www.mayoclinic.org/diseases-conditions/'
    },
    'symptoms': {
        'endpoint': '/symptoms/index',
        'search_endpoint': '/symptoms/'
    },
    'procedures': {
        'endpoint': '/tests-procedures/index',
        'search_endpoint': '/tests-procedures/'
    }
}

count = 0
urls = {}
for category, endpoints in resources.items():
    endpoint = endpoints['endpoint']
    search_endpoint = endpoints['search_endpoint']
    urls[category] = []
    for letter in LETTERS:
        all_urls = get_all_urls(BASE_URL, endpoint, letter, search_endpoint)

        unique_urls = set(all_urls)
        for url in unique_urls:
            if url.startswith("https://"):
                urls[category].append(url)
            else:
                urls[category].append(urljoin(BASE_URL, url))

urls['diseases'] = list(set(urls['diseases']))
urls['symptoms'] = list(set(urls['symptoms']))
urls['procedures'] = list(set(urls['procedures']))

with open('urls.json', 'w') as file:
    json.dump(urls, file)
