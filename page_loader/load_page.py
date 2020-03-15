import requests
import os
import re
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup


HTML_EXT = '.html'
RESOURCE_TAGS = (LINK, SCRIPT, IMG) = ('link', 'script', 'img')
RESOURCE_ATTRS = (HREF, SRC) = ('href', 'src')


def generate_file_name(full_address, is_asset=False):
    address_root, ext = os.path.splitext(full_address)
    address_root_parts = urlparse(address_root)
    scheme = address_root_parts.scheme
    if is_asset:
        ext = ext or HTML_EXT
        netloc = address_root_parts.netloc
        address = address_root.replace(f"{scheme}://{netloc}/", '', 1)
    else:
        ext = ''
        address = address_root.replace(f"{scheme}://", '', 1)
    address_parts = re.split(r"\W", address)
    return '-'.join(address_parts) + ext


def get_resource_attr_name(resource):
    tag = resource.name
    if tag == LINK:
        return HREF
    return SRC


def is_url_relative(url):
    return not bool(urlparse(url).netloc)


def select_local_resources(resources):
    local_resources = []
    for resource in resources:
        attr_name = get_resource_attr_name(resource)
        resource_url = resource.get(attr_name)
        if resource_url and is_url_relative(resource_url):
            local_resources.append(resource)
    return local_resources


def is_binary_resource(resource):
    return resource.name == IMG


def load_page(address, output):
    r = requests.get(address)
    if r.status_code != 200:
        print('Error')
        return

    page_content = r.text
    soup = BeautifulSoup(page_content, features="html.parser")
    page_resources = soup.find_all(RESOURCE_TAGS)
    local_resources = select_local_resources(page_resources)

    filename = generate_file_name(address)
    assets_folder_name = f"{filename}_files"
    assets_folder_path = os.path.join(output, assets_folder_name)
    if len(local_resources) and not os.path.exists(assets_folder_path):
        os.mkdir(assets_folder_path)

    for resource in local_resources:
        attr_name = get_resource_attr_name(resource)
        resource_url = resource[attr_name]
        full_resource_url = urljoin(address, resource_url)
        response = requests.get(full_resource_url)

        if is_binary_resource(resource):
            resource_content = response.content
            write_mode = 'wb'
        else:
            resource_content = response.text
            write_mode = 'w'

        resource_name = generate_file_name(full_resource_url, is_asset=True)
        resource_path = os.path.join(assets_folder_path, resource_name)
        with open(resource_path, write_mode) as f:
            f.write(resource_content)

        resource_full_name = os.path.join(assets_folder_name, resource_name)
        resource[attr_name] = resource_full_name

    output_path = os.path.join(output, filename + HTML_EXT)
    with open(output_path, 'w') as f:
        f.write(soup.prettify())
