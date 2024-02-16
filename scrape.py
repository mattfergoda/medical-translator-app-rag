import re

import requests
from bs4 import BeautifulSoup

URLS = [
    "https://www.health.harvard.edu/a-through-c",
    "https://www.health.harvard.edu/d-through-i",
    "https://www.health.harvard.edu/j-through-p",
    "https://www.health.harvard.edu/q-through-z",
]

definitions = {}
for url in URLS:
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    title_pattern = re.compile(r'<p><strong>(.*?): </strong>(.*?)</p>')
    remove_pattern = re.compile(r'^<a name="_GoBack"></a>\s*')

    # Find all the strong tags matching the pattern
    paragraphs =  soup.find_all("p")

    # Extract and print the titles and corresponding definitions
    for paragraph in paragraphs:
        match = title_pattern.search(str(paragraph))
        if match:
            title = re.sub(remove_pattern, '',match.group(1))
            definitions[title] = match.group(2)