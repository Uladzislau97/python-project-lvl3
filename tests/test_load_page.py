import requests
import tempfile
import os

import requests_mock

from page_loader import load_page


def test_load_page():
    with requests_mock.mock() as m:
        address = 'https://hexlet.io/courses'
        response_text = '<div>test</div>'
        m.get(address, text=response_text)

        with tempfile.TemporaryDirectory() as tmpdirname:
            load_page(address, tmpdirname)
            result_path = os.path.join(tmpdirname, 'hexlet-io-courses.html')

            with open(result_path, 'r') as f:
                assert f.read() == response_text


def test_load_page_with_local_resources():
    with requests_mock.mock() as m:
        host = 'https://hexlet.io'
        address = host + '/courses'

        with open('tests/fixtures/index.html', 'r') as f:
            m.get(address, text=f.read())
        
        with open('tests/fixtures/index.css', 'r') as f:
            request_address = host + '/assets/index.css'
            result_css_content = f.read()
            m.get(request_address, text=result_css_content)
        
        with open('tests/fixtures/index.js', 'r') as f:
            request_address = host + '/assets/index.js'
            result_js_content = f.read()
            m.get(request_address, text=result_js_content)
        
        with open('tests/fixtures/index.jpg', 'rb') as f:
            request_address = host + '/assets/index.jpg'
            result_bin_content = f.read()
            m.get(request_address, content=result_bin_content)
        
        with open('tests/fixtures/result.html', 'r') as f:
            result_html_content = f.read()
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            load_page(address, tmpdirname)

            result_html_path = os.path.join(tmpdirname, 'hexlet-io-courses.html')
            with open(result_html_path, 'r') as f:
                assert f.read() == result_html_content
            
            result_css_path = os.path.join(
                tmpdirname, 'hexlet-io-courses_files/assets-index.css'
            )
            with open(result_css_path, 'r') as f:
                assert f.read() == result_css_content
            
            result_js_path = os.path.join(
                tmpdirname, 'hexlet-io-courses_files/assets-index.js'
            )
            with open(result_js_path, 'r') as f:
                assert f.read() == result_js_content
            
            result_bin_path = os.path.join(
                tmpdirname, 'hexlet-io-courses_files/assets-index.jpg'
            )
            with open(result_bin_path, 'rb') as f:
                assert f.read() == result_bin_content
