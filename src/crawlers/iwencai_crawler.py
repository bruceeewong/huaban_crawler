# -*- coding:utf-8 -*-  
from enum import Enum
from os import stat
import sys
import json
import requests
import traceback
import re

sys.path.append('..')

from utils.file import File

class DataType(Enum):
    PLAIN = 1
    DATE = 2
    AVG = 3


class IWenCaiCrawler:
    RE_DATE =  r'(.*)\[(\d{8})\]'
    RE_AVG =  r'(.*)\[(\d{8}-\d{8})\]'

    def __init__(self):
        self.raw_data = {}
        self.normalized_data = []
        self.display_data = []

    def run(self):
        # answer = self.fetch_iwencai_data()
        json_data = self.read_iwencai_data()
        self.assemble_data(json_data)
        File.save_file('iwencai_processed_data.json', json.dumps(self.display_data, ensure_ascii=False), rel_path='data')
        

    def fetch_iwencai_data(self):
        """
        查询iwencai接口, 保存数据，并返回json值
        """
        url = 'http://www.iwencai.com/unifiedwap/unified-wap/v2/result/get-robot-data'
        headers = {
            "Host": "www.iwencai.com",
            "Content-Length": "928",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "hexin-v": "Aw2g7u-yUS4X3_UCkZa2s5cYFSKE6kNIyx2lkE-SSjsTWCPUFzpRjFtutXDc",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Origin": "http://www.iwencai.com",
            "Referer": "http://www.iwencai.com/unifiedwap/result?w=%E8%BF%9E%E7%BB%AD5%E5%B9%B4ROE%E5%A4%A7%E4%BA%8E20%25%EF%BC%8C%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%9A%84%E5%87%80%E5%88%A9%E6%B6%A6%E7%8E%B0%E9%87%91%E5%90%AB%E9%87%8F%E5%A4%A7%E4%BA%8E80%25%EF%BC%8C%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%9A%84%E6%AF%9B%E5%88%A9%E7%8E%87%E5%A4%A7%E4%BA%8E40%25%EF%BC%8C%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%9A%84%E5%B9%B3%E5%9D%87%E5%87%80%E5%88%A9%E6%B6%A6%E7%8E%B0%E9%87%91%E5%90%AB%E9%87%8F%E5%A4%A7%E4%BA%8E100%25%EF%BC%8C%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%9A%84%E8%B5%84%E4%BA%A7%E8%B4%9F%E5%80%BA%E7%8E%87%E5%B0%8F%E4%BA%8E60%25%EF%BC%8C%E8%BF%9E%E7%BB%AD5%E5%B9%B4%E7%9A%84%E5%88%86%E7%BA%A2%E6%AF%94%E4%BE%8B%E5%A4%A7%E4%BA%8E25%25&querytype=&issugs&sign=1623078519915",
            "Accept-Encoding": "gzip",
            "Accept-Language": "zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7,cy;q=0.6,la;q=0.5",
            "Cookie": "chat_bot_session_id=91b26a63a2288af39d9b2cda4c2f8da7; other_uid=Ths_iwencai_Xuangu_q4t3iqsgvhym58uuotkzf1kh5qrdecjn; cid=d027444bf3f8c01837cd6c6faadb45d31623076098; v=Aw2g7u-yUS4X3_UCkZa2s5cYFSKE6kNIyx2lkE-SSjsTWCPUFzpRjFtutXDc",
            "Connection": "keep-alive"
        }
        form = {
            'question': '连续5年ROE大于20%，连续5年的净利润现金含量大于80%，连续5年的毛利率大于40%，连续5年的平均净利润现金含量大于100%，连续5年的资产负债率小于60%，连续5年的分红比例大于25%',
            'perpage': '50',
            'page': '1',
            'secondary_intent': '',
            'log_info': {"input_type": "typewrite"},
            'source': 'Ths_iwencai_Xuangu',
            'version': '2.0',
            'query_area': '',
            'block_list': '',
            'add_info': {"urp": {"scene": 1, "company": 1, "business": 1}, "contentType": "json"},
        }
        print('>>>请求i问财接口')
        res = requests.post(url, data=form, headers=headers)
        if res.status_code != 200:
            print('>>>i问财接口返回码异常, status_code=' + res.status_code)
            res.raise_for_status()
            return

        print('>>>i问财接口返回成功')
        json_data = res.json()
        try:
            File.save_file('iwencai_answers.json', json.dumps(json_data, ensure_ascii=False), rel_path='data')
            print('>>>i问财接口数据保存成功')
        except IOError:
            print('写入文件失败')
            traceback.print_exc()

        # 返回查询结果
        return json_data

    def assemble_data(self, answer):
        self.raw_data =  IWenCaiCrawler.get_table_data(answer)
        datas = self.raw_data.get('datas')
        for data in datas:
            normalized_one_data = self.normalize_data(data)
            self.normalized_data.append(normalized_one_data)
            self.display_data.append(IWenCaiCrawler.process_display_data(normalized_one_data))
        return

    @staticmethod
    def read_iwencai_data():
        return File.read_file('iwencai_answers.json',  rel_path='data', type='json')

    @staticmethod
    def get_table_data(json_data):
        data_deep_inside = json_data['data']['answer'][0]['txt'][0]['content']['components'][0]['data']
        return {
            'columns': data_deep_inside['columns'],
            'datas': data_deep_inside['datas'],
        }

    @staticmethod
    def check_data_type(key):
        if re.match(IWenCaiCrawler.RE_DATE, key):
            return DataType.DATE
        elif re.match(IWenCaiCrawler.RE_AVG, key):
            return DataType.AVG
        else:
            return DataType.PLAIN

    @staticmethod
    def process_key_value(key, value):
        """
        将i问财的key,value处理成结构化数据
        """
        # 如果形如　\w+[yyyymmdd]　的，解析出　{label date value}
        # 否则返回　｛ label value}
        data_type = IWenCaiCrawler.check_data_type(key)
        if (data_type == DataType.DATE):
            result = re.match(IWenCaiCrawler.RE_DATE, key)
            label = result.group(1)
            date = result.group(2)
            return {
                'label': label,
                'type': data_type,
                'value': value,
                'metadata': {
                    'date': date,
                },
            }
        elif (data_type == DataType.AVG):
            result = re.match(IWenCaiCrawler.RE_AVG, key)
            label = result.group(1)
            date_range = result.group(2)
            return {
                'label': label,
                'type': data_type,
                'value': value,
                'metadata': {
                    'date_range': date_range,
                },
            }
        else:
            return {
                'label': key,
                'type': data_type,
                'value': value,
                'metadata': None,
            }

    @staticmethod
    def normalize_data(dict_data):
        result = []
        for key in dict_data:
            value = dict_data[key]
            item = IWenCaiCrawler.process_key_value(key, value)
            result.append(item)
        return result

    @staticmethod
    def process_display_data(normalized_data):
        """
        将i问财数据处理成要展示的数据结构
        """
        result = {}
        for item in normalized_data:
            new_label = item.get('label')
            new_type = item.get('type').value
            new_value = item.get('value')
            new_metadata = item.get('metadata')
            
            if new_type == DataType.DATE:
                date = new_metadata.get('date')
                if new_label not in result:
                    result[new_label] = {
                        'type': new_type,
                        'value': {
                            date: new_value
                        }
                    }
                else:
                    result[new_label]['value'].update({ date: new_value })
            elif new_type == DataType.AVG:
                date_range = new_metadata.get('date_range')
                result[new_label] = {
                    'type': new_type,
                    'value': {
                        date_range: new_value
                    }
                }
            else:
                result[new_label] = {
                    'type': new_type,
                    'value': new_value
                }

        return result