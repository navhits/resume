# This is not in use anymore but I still keep this here for reference
import os
from base64 import b64decode
import requests
from seleniumwire import webdriver


def interceptor(request):
    request.headers['CF-Access-Client-Id'] = os.getenv('CF_ACCESS_CLIENT_ID')
    request.headers['CF-Access-Client-Secret'] = os.getenv('CF_ACCESS_CLIENT_SECRET')

class Html2Pdf:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.request_interceptor = interceptor
    
    def __init__(self, url: str) -> None:
        self.url = url

    def convert(self) -> bytes:
        self.driver.get(self.url)
        properties = {
            "path": 'naveen.pdf',
            "paperWidth": 8.3,
            "paperHeight": 11.7,
            "printBackground": True,
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0
        }

        page_print = self.driver.execute_cdp_cmd("Page.printToPDF", properties)

        encoded_data = page_print['data']

        bytes_ = b64decode(encoded_data, validate=True)
        file_name = 'naveen-resume.pdf'
        if bytes_[0:4] != b'%PDF':
            return 'Missing the PDF file signature'

        with open(file_name, 'wb') as f:
            f.write(bytes_)

        return file_name

if __name__ == '__main__':
    file_name = Html2Pdf(url=f"{os.getenv('DEPLOYMENT_URL')}/resume").convert()


    headers = {
        'x-api-key': os.getenv('API_KEY'),
        'accept': 'application/json',
    }

    cookies = {
        'source' : os.getenv('SOURCE')
    }

    files={'file': (file_name, open(file_name,'rb'), 'application/pdf')}
    
    res = requests.post("https://api.navs.page/drive/upload", headers=headers,
                files=files, cookies=cookies)

    print(f"Status code: {res.status_code}")
    url = res.json().get('url')
    if url:
        print(f"URL: {url}")
    else:
        print(f"Error: {res.content}")
