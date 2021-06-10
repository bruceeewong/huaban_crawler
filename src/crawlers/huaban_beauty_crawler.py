# -*- coding:utf-8 -*-  
import requests
from requests import HTTPError
from parsel import Selector
import os
import json
import js2xml
import datetime
import traceback
import shutil
import urllib


def save_result(filename, content, path=None):
    filepath = os.getcwd()
    if isinstance(path, str):
        filepath += '/' + path + '/'
    if not os.path.isdir(filepath):
        os.mkdir(filepath)

    mode = 'a'
    full_path = filepath + filename
    if os.path.isfile(full_path):
        mode = 'w'

    with open(full_path, mode, encoding='utf-8') as f:
        f.write(content)


def get_pin_ids(json_data):
    if not isinstance(json_data.get('pins'), list):
        return []
    return list(map(lambda x: x.get('pin_id'), json_data.get('pins')))


def now():
    return str(datetime.datetime.now())


def fetch_pin_info():
    url = 'https://huaban.com/favorite/beauty'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Accept': 'application/json',
        'X-Request': 'JSON',
        'X-Requested-With': 'XMLHttpRequest'
    }
    params = {
        'kpl6mrdd': '',
        'max': '3970882367',
        'limit': '20',
        'wfl': '1',
    }
    z = requests.get(url, params=params, headers=headers)
    save_result('huaban_beauty.json', z.text, path='debug')
    return z.json()


def fetch_beauty_by_pin(pin_id):
    url_prefix = 'https://huaban.com/pins/'
    url = url_prefix + str(pin_id)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }

    res = requests.get(url, headers=headers)
    sel = Selector(text=res.text)
    # 抓取包含目标数据的 script
    return sel.xpath("//script[contains(., 'app.page = app.page')]/text()").extract_first()


def parse_js_code(js_code):
    save_result('js_code.js', js_code, path='debug')
    return js2xml.parse(js_code)


def get_img_keys(xml_code):
    save_result('xml_code.xml', js2xml.pretty_print(xml_code), path='debug')
    return xml_code.xpath('//property[@name="file"]/object/property[@name="key"]/string/text()')


def get_img_url(img_key):
    return 'http://hbimg.huabanimg.com/{img_key}_fw658/format/webp'.format(img_key=img_key)


def get_img_urls(img_keys):
    return list(set(map(lambda key: get_img_url(key), img_keys)))


def fetch_img_keys_by_pin(pin_id):
    print('>>> start fetching pin_id: ' + str(pin_id) + ' time: ' + now())
    try:
        js_code = fetch_beauty_by_pin(pin_id)
        xml_code = parse_js_code(js_code)
        img_keys = get_img_keys(xml_code)
        # img_urls = get_img_urls(keys)
        print('>>>>>> fetching img_keys succeeded, len: ' + str(len(img_keys)))
        return img_keys
    except Exception:
        print('>>>>>> fetching img_keys failed')
        traceback.print_exc()
    finally:
        print('<<< finish fetching pin_id: ' + str(pin_id) + ' time: ' + now())


def save_img(stream, dirname='whatever', filename='default', ext='webp'):
    filedir = os.getcwd() + '/imgs/' + dirname
    if not os.path.isdir(filedir):
        os.mkdir(filedir)
    filepath = filedir + '/' + filename + '.' + ext
    with open(filepath, 'wb') as file:
        shutil.copyfileobj(stream, file)


def save_all_imgs(pin_imgs, path='imgs'):
    for pin_id in pin_imgs:
        print('>>> fetching imgs by pin: ' + pin_id + ' time: ' + now())
        img_keys = pin_imgs.get(pin_id)
        for key in img_keys:
            url = get_img_url(key)
            try:
                filedir = os.getcwd() + '/' + path + '/' + pin_id
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                filepath = filedir + '/' + key + '.' + 'webp'
                urllib.request.urlretrieve(url, filepath)
                print('>>>>>> fetching img: ' + url + ' succeed')
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print('>>>>>> fetching img: ' + url + ' 404')
                else:
                    print('>>>>>> fetching img: ' + url + ' failed')
            except Exception as e:
                print('>>>>>> fetching img: ' + url + ' failed')
                traceback.print_exc()
        print('<<< finished fetching imgs by pin: ' + pin_id + ' time: ' + now())


def fetch_huaban_beauty_img_keys_by_pin(pin_ids):
    result = {}
    for pin_id in pin_ids:
        imgs_urls = fetch_img_keys_by_pin(pin_id)
        result[pin_id] = imgs_urls
    save_result('pin_imgs.json', json.dumps(result), path='data')


def main():
    """
    爬取花瓣网所有美女采集板的美女图片
    link: https://huaban.com/favorite/beauty/
    """
    pin_imgs_filepath = os.getcwd() + '/data/' + 'pin_imgs.json'

    if not os.path.isfile(pin_imgs_filepath):
        # 如果没有数据，重新爬
        json_data = fetch_pin_info()
        pin_ids = get_pin_ids(json_data)
        fetch_huaban_beauty_img_keys_by_pin(pin_ids)

    # 下载图片到本地
    with open(pin_imgs_filepath) as data:
        save_all_imgs(json.load(data), path='imgs')


if __name__ == '__main__':
    main()
