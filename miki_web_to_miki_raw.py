from DrissionPage import ChromiumPage
import re
from urllib.parse import unquote
import json
from pymongo import MongoClient
import requests
from qiniu import Auth, BucketManager, put_data
# from datetime import datetime
import logging
import os

# category = "shoes"     
category = "tops"     
# category = "outer"     
# category = "bottoms"  
# ---------------------

#-------------------------------------- LOG SETTING --------------------------------------
# Get the current script's filename with extension
script_name_with_extension = os.path.basename(__file__)
# Optionally, you can remove the extension if needed
script_name = os.path.splitext(script_name_with_extension)[0]
# Construct the log file path using the script's name
log_local_path = f'log/{script_name}.log'

if not os.path.exists(log_local_path):
    os.makedirs(os.path.dirname(log_local_path), exist_ok=True)
# 设置日志配置
logging.basicConfig(filename=log_local_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# 日志记录示例
logging.info('----------------------------Start of Program----------------------------')
#-------------------------------------- LOG SETTING --------------------------------------


# MongoDB连接配置
uri = "mongodb+srv://tangmx:Wlswn1587@product.etigdqd.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)  # 修改为您的MongoDB连接字符串
db = client['product']  # 替换为您的数据库名
raw_mikihouse_collection = db['mikihouse_raw']  # 替换为您的集合名

# 七牛链接配置
access_key = 'x24JShklQMqX2DdfxvT3a1SLLTicmSxmsqBry7ju'
secret_key = 'IrxgSwdOdhHuvy01u2KALG6hoUbHFNzOpQ7Oh1Vd'
q = Auth(access_key, secret_key)
bucket = BucketManager(q)
bucket_domain = 'sc75fiq49.hd-bkt.clouddn.com'
bucket_name = 'zoms'
# 获取当前时间并格式化为字符串
# current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
# key = f'products/lulu/product_ids/productIDs_{current_time}.txt'

def get_latest_file_contents(bucket_domain, bucket_name, access_key, secret_key, prefix):
    # 初始化授权和BucketManager
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)

    # 列出存储桶中的所有文件
    limit = 1000
    delimiter = None
    marker = None

    ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    if ret is None:
        print("Failed to list bucket:", info)
        return None

    # 查找最新的文件
    latest_file = None
    latest_date = None
    file_list = ret.get('items', [])
    for item in file_list:
        filename = item['key']
        # match = re.search(r'productIDs_(\d{8}_\d{6})\.txt', filename)
        match = re.search(r'productURLs_(\d{8})_(\d{6})\.txt', filename)
        if match:
            file_date = match.group(1)
            if latest_date is None or file_date > latest_date:
                latest_date = file_date
                latest_file = filename

    # 如果找到最新文件，生成下载链接并返回内容
    if latest_file:
        print("Latest file:", latest_file)
        # 生成下载URL
        # base_url = f'http://{bucket_name}.qiniudn.com/{latest_file}'
        base_url = 'http://%s/%s' % (bucket_domain, latest_file)
        private_url = q.private_download_url(base_url, expires=3600)
        # print(private_url)
        # print(base_url)
        
        # 下载文件内容
        response = requests.get(private_url)
        # print(response.status_code)
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to download the latest file.")
            return None
    else:
        print("No matching files found.")
        return None

# def decode_url_encoded_strings(input_string):
#     regex = re.compile(r'(%[0-9A-Fa-f]{2})+')
#     decoded_string = regex.sub(lambda match: unquote(match.group()), input_string)
#     # 去掉特殊符号* # $...
#     decoded_string = re.sub(r'[*#$]', '', decoded_string)
#     # # 4" 转换成 4\"
#     # pattern1 = r'("productName":"[^"]*\b\d+)(")'
#     # decoded_string = re.sub(pattern1, r'\1\\"', decoded_string)
#     # # 25"" 转换成 25\""
#     # pattern2 = r'(\d+)("")'
#     # decoded_string = re.sub(pattern2, r'\1\\""', decoded_string)
#     return decoded_string

#---------------------------------------
# 主程序入口
#---------------------------------------
qiniu_prefix = f"products/mikihouse/product_urls/{category}/"
product_urls_str = get_latest_file_contents(bucket_domain, bucket_name, access_key, secret_key, qiniu_prefix)
product_urls = product_urls_str.strip().split('\n')
for p_url in product_urls:
    try:
        page = ChromiumPage()
        # page.get(product_urls[0])
        page.get(p_url)
        product_name = page.s_ele("xpath://h1[@class='product-single__title']").text
        brand = page.s_ele("xpath://*[@id='ProductSection-main-product']/div[2]/div[2]/div/div/div[1]/div[1]/dd").text
        price_text = page.s_ele("xpath://span[@class='price-item price-item--regular']").text
        price = float(re.sub(r'[^\d.]', '', price_text))
        product_code = page.s_ele("xpath://*[@id='ProductSection-main-product']//form/p[1]").text

        thumbnails = page.eles("xpath://*[@id='js-medias__gallery']//img")
        # Check if thumbnails are found and interact with the last one
        if thumbnails:
            last_thumbnail = thumbnails[-1]
            last_thumbnail.click()  # Clicks the last thumbnail
        else:
            print('No thumbnails found')
        thumbnail_count = len(thumbnails)
        base_xpath = "xpath://*[@id='js-medias__gallery']/div[{}]/img"
        img_urls = []
        for i in range(1, thumbnail_count + 1):
            img_xpath = base_xpath.format(i)
            img_src = page.s_ele(img_xpath).attr('src')  
            if img_src:
                img_urls.append(img_src)

        itemList = page.eles("xpath://*[@id='option2']//*[@class='option-selector']")
        item_info = []
        for item in itemList:
            itemSizeText = item.ele("xpath:.//label")
            itemSize = page.run_js("return arguments[0].firstChild.textContent.trim();", itemSizeText)
            itemPrice = item.ele("xpath:.//label/span").text
            itemJancode = item.ele("xpath:.//div").attr('data-select-option')
            # 将获取到的文本和属性值存入itemInfo数组
            item_info.append((itemSize, itemPrice, itemJancode))
            
        product_color = page.ele("xpath://div[@class='colorContent-imageBox']//input[@type='radio' and @checked]").attr('value')
        product_url = page.url

        sku = product_code + ' ' + product_color

        product_details_eles = page.eles(".product_info product-single__description")
        p_details = [item.text for item in product_details_eles]
        # Join all texts with a newline character
        product_details = '\n'.join(p_details)
                    
        # print(product_name, brand, price, product_code, thumbnail_count, img_urls[0], item_info[0], product_color, product_url, sku, product_details)

        document = {
            'product_name': product_name,
            'category': category,
            'brand': brand,
            'price': price,
            'product_code': product_code,
            'img_urls': img_urls,
            'item_info': item_info,
            'product_color': product_color,
            'product_url': product_url,
            'sku': sku,
            'product_details': product_details
        }

        result = raw_mikihouse_collection.update_one(
                {'sku': sku},
                {'$set': document},
                upsert=True
            )
        if result.matched_count:
            print("Document matched.")
            if result.modified_count:
                print("Document updated.")
            else:
                print("Document matched but not updated (no changes needed).")
        else:
            if result.upserted_id is not None:
                print(f"New document inserted with ID: {result.upserted_id}")
            else:
                print("No document matched and no document inserted.")
                
    except Exception as e:
        print(f'An error occurred while processing {p_url}: {e}')
        # print(f'An error occurred while processing {product_urls[0]}: {e}')

page.close()