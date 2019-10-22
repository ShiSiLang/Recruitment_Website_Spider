# coding=utf-8
# @ Author: TianHao
# @ Python: Python3.6.1
# @ Date: 2019/10/22 11:07
# @ Desc 拉钩职位信息
import requests
from lxml import etree
import pymysql


def get_job_id():
    sql = "SELECT DISTINCT(positionId) FROM lagou"
    conn = pymysql.connect(host="cdb-8b46fhc0.bj.tencentcdb.com", port=10204, user="root", password="Tianhao0311",
                           db="jobs")
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_info(job_id):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        "Referer": "https://www.lagou.com/jobs/list_%E6%B5%8B%E8%AF%95%E5%B7%A5%E7%A8%8B%E5%B8%88?labelWords=&fromSearch=true&suginput="
    }
    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "HMI7Q235P0TM7RSD"
    proxyPass = "78B667821AFF7087"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    url = "https://www.lagou.com/jobs/{}.html".format(job_id)
    response = requests.get(url, headers=headers,proxies=proxies)
    e = etree.HTML(response.text)
    describe = "".join(e.xpath('//div[@class="job-detail"]//text()')).strip('\n ')
    com_type = e.xpath('//h4[@class="c_feature_name"]/text()')[0]
    com_level = e.xpath('//h4[@class="c_feature_name"]/text()')[1]
    com_people = e.xpath('//h4[@class="c_feature_name"]/text()')[2]
    params = (job_id,describe,com_type,com_level,com_people)

def save_to_mysql(params):
    """
    存储Mysql数据库
    :param params: 字段数据
    :return:
    """
    conn = pymysql.connect(host="cdb-8b46fhc0.bj.tencentcdb.com", port=10204, user="root", password="Tianhao0311",
                           db="jobs")
    cursor = conn.cursor()
    sql = "insert into lagou_detail(job_id,describe,com_type,com_level,com_people) values (%s,%s,%s,%s,%s)"
    cursor.execute(sql, params)
    conn.commit()


if __name__ == '__main__':
    job_id_list = get_job_id()
    for i in job_id_list:
        get_info(i[0])
