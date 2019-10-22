# coding=utf-8
# @ Author: TianHao
# @ Python: Python3.6.1
# @ Date: 2019/10/15 10:56
# @ Desc 抓取前程无忧51job 职位列表
import pymysql
import requests
import demjson
from lxml import etree

from config import city_list_51job

headers = {
    "Sec-Fetch-Mode": "no-cors",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
}


def get_city_list():
    """
    获取城市编码，运行并将结果存储在config.py文件中(一次性)
    :return:
    """
    city = {}
    url = "https://js.51jobcdn.com/in/js/h5/dd/d_jobarea.js"
    response = requests.get(url, headers=headers).text
    temp = response[response.find("var allProvinceAndArea="):]
    result = temp[:temp.find(";var")].strip("var allProvinceAndArea=")
    city_dict = demjson.decode(result)
    for key, value in city_dict.items():
        for i in range(len(value)):
            city[value[i]["v"]] = value[i]["k"]
    return city


def get_info(city, key, page=1):
    """
    请求数据并存储
    :param city:  城市名--> str
    :param key: 职位关键词 --> str
    :param page: 页码 -->int（默认）
    :return: None
    """
    url = "https://m.51job.com/search/joblist.php?jobarea={}&keyword={}&keywordtype=2&pageno={}".format(city, key, page)
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    h = etree.HTML(response.text)
    divs = h.xpath('//div[@class="items"]/a')
    for div in divs:
        detail_url = div.xpath('./@href')[0]
        job = ''.join(div.xpath('.//h3//text()'))
        salary = div.xpath('.//em//text()')[0]
        company = div.xpath('.//aside//text()')[0]
        addr = div.xpath('.//i//text()')[0]
        education, experience = get_detail(detail_url)
        params = (key, job, salary, company, addr, experience, education)
        save_to_mysql(params)


def get_detail(url):
    """
    获取职位列表的学历已经经验字段
    :param url: 职位详细地址
    :return: 职位、经验字段数据
    """
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    h = etree.HTML(response.text)
    try:
        education = h.xpath('//span[@class="s_x"]/text()')[0]
    except:
        education = -1
    try:
        experience = h.xpath('//span[@class="s_n"]/text()')
    except:
        experience = "无"
    return education, experience


def save_to_mysql(params):
    """
    存储Mysql数据库
    :param params: 字段数据
    :return:
    """
    conn = pymysql.connect(host="127.0.0.1", port=10204, user="root", password="123456",
                           db="jobs")
    cursor = conn.cursor()
    sql = "insert into boss(keyword, job, salary, company, addr, experience, education) values (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql, params)
    conn.commit()


if __name__ == '__main__':
    key = input("请输入职位名称：")
    city_name = input("请输入城市名称：")
    try:
        city = city_list_51job[city_name]
        get_info(key=key, city=city)
    except:
        print("您输入的城市不存在")
