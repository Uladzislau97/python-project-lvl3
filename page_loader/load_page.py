import requests
import os
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def generate_page_name(full_address):
    address_root, _ = os.path.splitext(full_address)
    scheme = urlparse(address_root).scheme
    address = address_root.replace(f"{scheme}://", '', 1)
    address_parts = re.split(r"\W", address)
    return '-'.join(address_parts)


def load_page(address, output):
    r = requests.get(address)
    if r.status_code != 200:
        print('Error')
        return

    page_content = r.text
    page_name = generate_page_name(address)
    output_path = os.path.join(output, f"{page_name}.html")
    with open(output_path, 'w') as f:
        f.write(page_content)
