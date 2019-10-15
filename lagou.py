# coding=utf-8
# @ Author: TianHao
# @ Python: Python3.6.1
# @ Date: 2019/10/15 13:56
# @ Desc 拉勾网职位数据抓取
from urllib import parse
import pymysql
import requests

"""
需要增加存储字段，mysql或者excel
"""
def get_info(key, city, page=1):
    """
    :param key: 关键字 -->str
    :param city: 城市 --> str
    :param page: 页码
    :return:
    """
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.lagou.com/jobs/list_{}/p-city_0?&cl=false&fromSearch=true&labelWords=&suginput='.format(
            parse.quote(key)),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    start_url = "https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput=".format(parse.quote(key))
    s = requests.Session()
    s.get(start_url, headers=headers)
    cookies = s.cookies

    url = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"
    if page == 1:
        params = {
            "first": "true",
            "pn": str(page),
            "kd": key,
        }
    else:
        params = {
            "first": "false",
            "pn": page,
            "kd": key,
        }
    response = s.post(url, data=params, headers=headers, cookies=cookies).json()
    if response["success"]:
        job_list = response["content"]["positionResult"]["result"]
        for i in job_list:
            job = i["positionName"]
            salary = i["salary"]
            company = i["companyShortName"]
            addr = i["city"]
            experience = i["workYear"]
            education = i["education"]
            params = (key, job, salary, company, addr, experience, education)


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
    get_info("人事", "北京")
