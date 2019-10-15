# coding=utf-8
# @ Author: TianHao
# @ Python: Python3.6.1
# @ Date: 2019/10/14 16:30
# @ Desc boss直聘职位信息抓取
import pymysql
import requests
from lxml import etree
from .config import city_list_boss



def get_city_code():
    """
    获取城市列表
    :return: city_list -->List
    """
    url = "https://www.zhipin.com/wapi/zpCommon/data/city.json"
    response = requests.get(url).json()
    result = {}
    if response["code"] == 0:
        cityList = response["zpData"]["cityList"]
        for city in cityList:
            result[city["name"]] = city["code"]
        result["全国"] = 100010000
        return result
    else:
        print("请求失败")


proxies = {
    "http": "http://58.218.200.248:9196",
    "https": "https://58.218.200.214:9015",
}
headers = {
    'Accept': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Referer': 'https://www.zhipin.com/',
    'X-Requested-With': "XMLHttpRequest",
    "cookie": "lastCity=101020100; JSESSIONID=""; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1532401467,1532435274,1532511047,1532534098; __c=1532534098; __g=-; __l=l=%2Fwww.zhipin.com%2F&r=; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fc101020100-p100103%2F; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1532581213; __a=4090516.1532500938.1532516360.1532534098.11.3.7.11"
}


def get_info(key, city, page=1):
    """
    :param key: 搜索职位关键词
    :param city: 城市编码
    :param page: 页码
    :return: None
    """
    url = "http://www.zhipin.com/mobile/jobs.json?page={}&city=c{}&query={}".format(page, city, key)
    response = requests.get(url, verify=False, headers=headers, proxies=proxies).json()
    has_more = response["hasMore"]
    h = etree.HTML(response["html"])
    liList = h.xpath('//li[@class="item"]')
    for li in liList:
        job = ''.join(li.xpath('.//h4/text()'))
        salary = ''.join(li.xpath('.//span[@class="salary"]/text()'))
        company = ''.join(li.xpath('.//div[@class="name"]/text()'))
        addr = li.xpath('.//em/text()')[0]
        try:
            experience = li.xpath('.//em/text()')[1]
        except:
            experience = "无"
        try:
            education = li.xpath('.//em/text()')[2]
        except:
            education = -1
        params = (key, job, salary, company, addr, experience, education)
        save_to_mysql(params)

    if has_more:
        page += 1
        print("正在请求第{}页".format(page))
        get_info(key, city, page=page)


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
        city = city_list_boss[city_name]
        get_info(key=key, city=city)
    except:
        print("您输入的城市不存在")
