# -*- coding:utf-8 -*-
"""
NUAA新教务系统模拟登录及课表获取

@Author: miaotony
@Version: V0.2.1.20191012
@UpdateLog:
    V0.2.1.20191012 增加UA列表，增加BeautifulSoup提取姓名学号，优化代码结构，为下一步解析课表做准备
    V0.2.0.20191010 成功登录教务系统，并成功获取个人或班级课表，但还未进行提取
    V0.1.1.20190910 加入未登录成功或过快点击的判断
    V0.1.0.20190909 尝试登录新教务系统成功，仅登录而已

"""

import requests
import re
from bs4 import BeautifulSoup
from hashlib import sha1
import time
import random

session = requests.Session()
UAs = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201",
    "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
]
headers = {
    "User-Agent": UAs[random.randint(0, len(UAs) - 1)],  # random UA
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}
# 设置session的请求头信息
session.headers = headers
host = r'http://aao-eas.nuaa.edu.cn'  # 'http://miao.free.idcfengye.com'  #


def aao_login(stuID, stuPwd, retry_cnt=3):
    """
    登录新教务系统
    :param stuID: 学号
    :param stuPwd: 密码
    :param retry_cnt: 登录重试次数
    :return: name: {str} 姓名(学号)
    """
    while retry_cnt >= 0:
        r1 = session.get(host + '/eams/login.action')
        # print(r1.text)

        temp_key_match = re.compile(r"CryptoJS\.SHA1\(\'([0-9a-zA-Z\-]*)\'")
        # 搜索密钥
        if temp_key_match.search(r1.text):
            print("Search key OK!\n")
            temp_key = temp_key_match.search(r1.text).group(1)
            # print(temp_key)
            postPwd = temp_key + stuPwd
            # print(postPwd)

            # 开始进行SHA1加密
            s1 = sha1()  # 创建sha1对象
            s1.update(postPwd.encode())  # 对s1进行更新
            postPwd = s1.hexdigest()  # 加密处理
            # print(postPwd)  # 结果是40位字符串

            # 开始登录啦
            # while retry_cnt >= 0:
            postData = {'username': stuID, 'password': postPwd}
            r2 = session.post(host + '/eams/login.action', data=postData)
            if r2.status_code == 200 or r2.status_code == 302:
                # print(r2.text)
                temp_key = temp_key_match.search(r2.text)
                if temp_key:  # 找到密钥说明没有登录成功，需要重试
                    print("ID or Password ERROR! Login ERROR!\n")
                    temp_key = temp_key.group(1)
                    print(temp_key)
                    exit(2)
                elif re.search(r"ui-state-error", r2.text):  # 过快点击
                    print("ERROR! 请不要过快点击!\n")
                    time.sleep(3)
                    retry_cnt -= 1
                    # session.headers["User-Agent"] = UAs[1]  # random.randint(0, len(UAs)-1)  # 换UA也不行
                    exit(3)
                else:
                    temp_soup = BeautifulSoup(r2.text.encode('utf-8'), 'lxml')
                    name = temp_soup.find('a', class_='personal-name').string.strip()
                    print("Login OK!\nHello, {}!".format(name))
                    return name
            else:
                print("Login ERROR!\n")
                exit(1)
        else:
            print('Search key ERROR!\n')
            exit(1)


def getCourseTable(choice=0):
    """
    获取课表
    :param choice: 0 for std, 1 for class.个人课表or班级课表，默认为个人课表。
    :return:courseTable: {Response} 课表html响应
    """
    courseTableResponse = session.get(host + '/eams/courseTableForStd.action')
    # print(courseTableResponse.text)
    # print(session.cookies.get_dict())

    temp_ids_match = re.compile(r"bg\.form\.addInput\(form,\"ids\",\"([0-9]*)\"")
    temp_ids = temp_ids_match.findall(courseTableResponse.text)
    if temp_ids:
        print(temp_ids)  # [0] for std, [1] for class.

        # postData_course = {
        #     "ignoreHead": "1",
        #     "setting.kind": "std",
        #     "startWeek": "",
        #     "project.id": "1",
        #     "semester.id": "62",
        #     "ids": "68175"
        # }

        if choice == 1:  # 班级课表
            ids = temp_ids[1]
            kind = "class"
        else:  # 个人课表   choice == 0
            ids = temp_ids[0]
            kind = "std"

        courseTable_postData = {
            "ignoreHead": "1",
            "setting.kind": kind,
            "startWeek": "",  # None for all weeks
            "project.id": "1",
            "semester.id": session.cookies.get_dict()['semester.id'],
            "ids": ids
        }
        courseTable = session.post(host + '/eams/courseTableForStd!courseTable.action',
                                   data=courseTable_postData)
        print(courseTable.text)
        # print(session.cookies.get_dict())
        return courseTable
    else:
        print("Get ids ERROR!")
        exit(4)


if __name__ == "__main__":
    # 学号及密码
    stuID = r"0417"
    stuPwd = r""
    retry_cnt = 3  # 登录重试次数

    temp_time = time.time()
    name = aao_login(stuID, stuPwd, retry_cnt)
    print('\nMiao~下面开始获取课表啦！\n')
    courseTable = getCourseTable(choice=0)
    print('累计用时：', time.time() - temp_time, 's')
