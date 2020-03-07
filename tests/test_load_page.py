import requests
import tempfile
import os

import requests_mock

from page_loader import load_page


def test_load_page():
    address = 'https://hexlet.io/courses'
    response_text = '<div>test</div>'
    temp_dir = tempfile.TemporaryDirectory()

    with requests_mock.mock() as m:
        m.get(address, text=response_text)

        with tempfile.TemporaryDirectory() as tmpdirname:
            load_page(address, tmpdirname)
            result_path = os.path.join(tmpdirname, 'hexlet-io-courses.html')

            with open(result_path, 'r') as f:
                assert f.read() == response_text
