from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver  # SWAP standard webdriver
from seleniumwire.utils import decode

driver = webdriver.Chrome()
driver.get("https://app.powerbi.com/view?r=eyJrIjoiMzJjOTA2MjYtNjA0My00ZGU4LWE5MDktYWQyODRhZWNiM2MyIiwidCI6IjlkMGRjYTFlLTAzODQtNGRhNS1hNWMwLWQxNGI5YWExZDk5ZCIsImMiOjN9&wmode=transparent")

import time
time.sleep(15)  # WAIT for Power BI to load and fire its data requests

# SCAN all network requests made by Power BI
for request in driver.requests:
    if "querydata" in request.url or "executeSemanticQuery" in request.url:
        print(request.url)
        if request.response:
            try:
                body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                print(body.decode('utf-8'))
            except Exception as e:
                print(f"Error decoding body: {e}")