import requests
import os
import re
import logging
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
from progress.bar import Bar


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


def download_file(address, binary=False):
    r = requests.get(address)
    if r.status_code != 200:
        msg = f"Request to {address} returned: {r.status_code} {r.reason}"
        logging.error(msg)
        raise ConnectionError(msg)
    return r.content if binary else r.text


def save_to_file(write_path, content, binary=False):
    mode = 'wb' if binary else 'w'
    try:
        with open(write_path, mode) as f:
            f.write(content)
    except FileNotFoundError:
        msg = f"Invalid path to save file: {write_path}"
        logging.error(msg)
        raise FileNotFoundError(msg)
    except PermissionError:
        msg = f"No permission to save file: {write_path}"
        logging.error(msg)
        raise PermissionError(msg)


def create_folder(folder_path):
    try:
        os.mkdir(folder_path)
    except FileNotFoundError:
        msg = f"Invalid path for local resources folder: {folder_path}"
        logging.error(msg)
        raise FileNotFoundError(msg)
    except PermissionError:
        msg = f"No permission to create folder: {folder_path}"
        logging.error(msg)
        raise PermissionError(msg)


def load_page(address, output, logging_level):
    logging.basicConfig(level=logging_level)
    logging.debug(f"Donwload address: {address}")
    logging.debug(f"Output path: {output}")

    bar = Bar('Processing', max=5)

    page_content = download_file(address)
    bar.next()

    soup = BeautifulSoup(page_content, features="html.parser")
    page_resources = soup.find_all(RESOURCE_TAGS)
    local_resources = select_local_resources(page_resources)
    bar.next()

    filename = generate_file_name(address)
    assets_folder_name = f"{filename}_files"
    assets_folder_path = os.path.join(output, assets_folder_name)
    if len(local_resources) and not os.path.exists(assets_folder_path):
        logging.debug(
            f"Create folder for local files: {assets_folder_path}"
        )
        create_folder(assets_folder_path)
    bar.next()

    for resource in local_resources:
        attr_name = get_resource_attr_name(resource)
        resource_url = resource[attr_name]
        full_resource_url = urljoin(address, resource_url)

        logging.debug(f"Download resource: {full_resource_url}")
        is_binary = is_binary_resource(resource)
        resource_content = download_file(full_resource_url, is_binary)

        resource_name = generate_file_name(full_resource_url, is_asset=True)
        resource_path = os.path.join(assets_folder_path, resource_name)

        logging.debug(f"Save local resource as: {resource_path}")
        save_to_file(resource_path, resource_content, is_binary)

        resource_full_name = os.path.join(assets_folder_name, resource_name)
        resource[attr_name] = resource_full_name
    bar.next()

    output_path = os.path.join(output, filename + HTML_EXT)
    result_page_content = soup.prettify()

    logging.debug(f"Save main page as: {output_path}")
    save_to_file(output_path, result_page_content)
    bar.next()
    bar.finish()
