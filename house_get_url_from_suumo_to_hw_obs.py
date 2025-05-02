#---------------------------------------------------------------------
# fetch urls from suumo website and store them into huawei obs
#---------------------------------------------------------------------
from DrissionPage import ChromiumPage
import re
from urllib.parse import unquote
import json
from pymongo import MongoClient
import requests
from qiniu import Auth, BucketManager, put_data
import logging
from datetime import datetime
import os
import time
from obs import ObsClient
from obs import PutObjectHeader
import traceback

#---------------------------- PARAMETER SETTING ----------------------------
# basic_url = "https://suumo.jp"
start_url = "https://suumo.jp/jj/bukken/ichiran/JJ010FJ001/?ar=030&bs=020&ta=13&jspIdFlg=patternShikugun&sc=13104&kb=1&kt=9999999&km=1&tb=0&tt=9999999&hb=0&ht=9999999&ekTjCd=&ekTjNm=&tj=0&kw=1&srch_navi=1"
label = "shinjuku_ikenya_shinchiku_0512"
objectKey = f"housenavi/urls/{label}.txt"

#---------------------------- LOG SETTING ----------------------------
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
script_name_with_extension = os.path.basename(__file__)
script_name = os.path.splitext(script_name_with_extension)[0]
log_local_path = f'log/{script_name}.log'

if not os.path.exists(log_local_path):
    os.makedirs(os.path.dirname(log_local_path), exist_ok=True)
logging.basicConfig(filename=log_local_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f'---------------------------- Start of Program at {current_time} ----------------------------')

#---------------------------- DATABASE SETTING ----------------------------
# Huawei OBS
hw_server = "https://obs.cn-east-3.myhuaweicloud.com"
hw_obs_client = ObsClient(access_key_id="FGIVK5I0CGIAYVCALHR1",
                          secret_access_key="CZ6cVGPVTD7pAangIc3aVg7fKNY1ldErGdhTaVrk", 
                          server=hw_server)
hw_bucket_name = "z-projects"

#---------------------------- FUNCTION DEFINITION ----------------------------
# Function: scroll to bottom of the web page
def scroll_to_bottom(page, max_attempts=30, sleep_time=3):
    attempts = 0
    old_position = 0
    new_position = None
    while attempts < max_attempts:
        # Scroll down by running JavaScript
        page.run_js('window.scrollTo(0, document.body.scrollHeight);')
        # Wait for the page to load
        time.sleep(sleep_time)
        # Check the current scroll position
        new_position = page.run_js('return window.pageYOffset;')
        
        # Check if the bottom of the page is reached
        if new_position == old_position:
            # print("Already reached the bottom of the page.")
            break  # Stop scrolling if the page position has not changed
        else:
            old_position = new_position
            attempts += 1
            # print(f"Scrolled to position: {new_position}")

#---------------------------- MAIN ENTRANCE ---------------------------- 
page = ChromiumPage()           
page.get(start_url+"&page=1&pc=100", retry=1, interval=3, timeout=5)
page_eles = page.eles('xpath://*[@id="js-sectionBody-main"]//div[2]//ol/li')
last_page = int(page_eles[-1].text)
print(last_page)

urls = []
for i in range(1, last_page + 1):
    target_url = start_url+"&pc=100"+f"&page={i}"
    print(target_url)
    
    page.get(target_url, retry=1, interval=3, timeout=5)

    while page.states.ready_state != 'complete':
        print("Waiting for the page to load completely...")
        time.sleep(1)          
    print("Page is fully loaded.")

    page.set.scroll.smooth(on_off=True)
    scroll_to_bottom(page)

    urls_eles = page.eles('xpath://*[@id="js-bukkenList"]//div[2]/div[1]/h2/a')
    new_urls  = [url.attr('href') for url in urls_eles]
    urls.extend(new_urls)

    print(f"Added {len(new_urls)} URLs. Total collected: {len(urls)}")

urls_content = '\n'.join(urls)

try:
    urls_bytes = urls_content.encode('utf-8')
    resp = hw_obs_client.putContent(hw_bucket_name, objectKey, urls_bytes)
    if resp.status < 300:
        print('Put Content Succeeded')
        print('requestId:', resp.requestId)
        print('etag:', resp.body.etag)
    else:
        print('Put Content Failed')
        print('requestId:', resp.requestId)
        print('errorCode:', resp.errorCode)
        print('errorMessage:', resp.errorMessage)
except:
    print('Put Content Failed')
    print(traceback.format_exc())
