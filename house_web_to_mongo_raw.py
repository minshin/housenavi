#---------------------------------------------------------------------
# get house info and store them into mongodb
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
from obs import GetObjectHeader
from obs import PutObjectHeader
import traceback


#---------------------------- PARAMETER SETTING ----------------------------
# basic_url = "https://suumo.jp"
# start_url = "https://suumo.jp/jj/bukken/ichiran/JJ010FJ001/?ar=030&bs=020&ta=13&jspIdFlg=patternShikugun&sc=13104&kb=1&kt=9999999&km=1&tb=0&tt=9999999&hb=0&ht=9999999&ekTjCd=&ekTjNm=&tj=0&kw=1&srch_navi=1"
# label = "shinjuku_ikenya_shinchiku_0512"
# objectKey = f"housenavi/urls/{label}.txt"

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

# MongoDB连接配置
uri = "mongodb+srv://tangmx:Wlswn1587@product.etigdqd.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)  
db = client['house']  
suumo_collection_raw = db['suumo_house_raw']  

#---------------------------- FUNCTION DEFINITION ----------------------------
# Function: scroll to bottom of the web page
# def scroll_to_bottom(page, max_attempts=30, sleep_time=3):



#---------------------------- MAIN ENTRANCE ---------------------------- 
# page = ChromiumPage()           
# page.get(start_url+"&page=1&pc=100", retry=1, interval=3, timeout=5)
# page_eles = page.eles('xpath://*[@id="js-sectionBody-main"]//div[2]//ol/li')
# last_page = int(page_eles[-1].text)
# print(last_page)

try:
    # 下载对象的附加头域
    headers = GetObjectHeader()
    downloadPath = 'data/2.txt'
    objectKey = 'housenavi/urls/tokyo_mansion_shinchiku_0512.txt'
    resp = hw_obs_client.getObject(hw_bucket_name, objectKey, downloadPath, headers=headers)

    if resp.status < 300:
        print('Get Object Succeeded')
        print('requestId:', resp.requestId)
    else:
        print('Get Object Failed')
        print('requestId:', resp.requestId)
        print('errorCode:', resp.errorCode)
        print('errorMessage:', resp.errorMessage)
except:
    print('Get Object Failed') 
    print(traceback.format_exc())
    
with open(downloadPath, 'r', encoding='utf-8') as f:
    house_urls = [line.strip() for line in f.readlines()]

page = ChromiumPage()
for h_url in house_urls:
    try:
        page.get(h_url)
        house_name_ele = page.s_ele("xpath://*[@id='js-normal_h1']/div[1]/h1/span[1]")
        house_name = house_name_ele.text if house_name_ele else ""
        
        house_price_ele             = page.s_ele("xpath://*[@id='js-normal_h1']/div[2]/span")
        house_price = house_price_ele.text if house_price_ele else ""                                                       
        
        house_brief_ele             = page.s_ele("xpath://*[@id='js-normal_h1']/div[3]/div/div")
        house_brief = house_brief_ele.text if house_brief_ele else ""
        house_location_ele          = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[1]/td/div/div")
        house_location = house_location_ele.text if house_location_ele else ""
        house_access_ele            = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[2]/td[1]")
        house_access = house_access_ele.text if house_access_ele else ""
        house_total_resident_ele    = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[2]/td[2]")
        house_total_resident = house_total_resident_ele.text if house_total_resident_ele else ""
        house_layout_ele            = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[3]/td[1]")
        house_layout = house_layout_ele.text if house_layout_ele else ""
        # house_area_ele              = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[3]/td[2]")
        
        # house_pre_price_ele         = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[4]/td/div/span")
        
        # house_turnkey_date_ele      = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[5]/td")
        
        # house_start_date_ele        = page.s_ele("xpath://*[@id='js-detailtopContents']/div[7]/div[2]/div/table/tbody/tr[6]/td")
        
        info = "\n".join([
            house_name,
            house_price, 
            house_brief, 
            house_location, 
            house_access, 
            house_total_resident, 
            house_layout, 
            # house_area,
            # house_pre_price, 
            # house_turnkey_date, 
            # house_start_date           
        ])
        
        
        # house_name_ele = page.ele('@|id=js-normal_h1')
        # house_name = house_name_ele.ele('h1').text
        
        if house_name is not None:
            print(info)
            
            
        else:
            print("no such title")

        
        # document = {
        #     'house_name': house_name
        # }
        
        # result = suumo_collection_raw.update_one(
        #         {'house_name': house_name},
        #         {'$set': document},
        #         upsert=True
        #     )
        # if result.matched_count:
        #     print("Document matched.")
        #     if result.modified_count:
        #         print("Document updated.")
        #     else:
        #         print("Document matched but not updated (no changes needed).")
        # else:
        #     if result.upserted_id is not None:
        #         print(f"New document inserted with ID: {result.upserted_id}")
        #     else:
        #         print("No document matched and no document inserted.")
                
    except Exception as e:
        print(f'An error occurred while processing {h_url}: {e}')

