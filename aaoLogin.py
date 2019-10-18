# -*- coding:utf-8 -*-
"""
NUAA新教务系统模拟登录及课表获取

@Author: miaotony
@Version: V0.3.0.20191017
@UpdateLog:
    V0.3.0.20191017 增加 课表解析，增加 班级、实践周匹配，优化代码结构
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
from requests_html import HTMLSession
import json

# session = HTMLSession()
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
    "User-Agent": UAs[1],  # UAs[random.randint(0, len(UAs) - 1)],  # random UA
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    # "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    # "Cookie":"GSESSIONID=F6052EDFBEF1E44EEE69375BA5F233CD;SERVERNAME=s2;JSESSIONID=F6052EDFBEF1E44EEE69375BA5F233CD;semester.id=62"
}
# 设置session的请求头信息
session.headers = headers
host = r'http://aao-eas.nuaa.edu.cn'


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

        temp_token_match = re.compile(r"CryptoJS\.SHA1\(\'([0-9a-zA-Z\-]*)\'")
        # 搜索密钥
        if temp_token_match.search(r1.text):
            print("Search token OK!\n")
            temp_token = temp_token_match.search(r1.text).group(1)
            # print(temp_token)
            postPwd = temp_token + stuPwd
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
                temp_key = temp_token_match.search(r2.text)
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
        # print(temp_ids)  # [0] for std, [1] for class.

        # postData_course = {
        #     "ignoreHead": "1",
        #     "setting.kind": "std",
        #     "startWeek": "",
        #     "project.id": "1",
        #     "semester.id": "62",
        #     "ids": "xxxxx"
        # }

        if choice == 1:  # 班级课表
            ids = temp_ids[1]
            kind = "class"
        else:  # 个人课表   choice == 0
            ids = temp_ids[0]
            kind = "std"

        courseTable_postData = {
            # "ignoreHead": "1",
            "setting.kind": kind,
            # "startWeek": "",  # None for all weeks
            # "project.id": "1",
            # "semester.id": session.cookies.get_dict()['semester.id'],
            "ids": ids
        }
        courseTable = session.get(host + r'/eams/courseTableForStd!courseTable.action',
                                  params=courseTable_postData)
        # courseTable = session.post(host + '/eams/courseTableForStd!courseTable.action',
        #                            data=courseTable_postData)

        # print(courseTable.text)
        # print(session.cookies.get_dict())
        return courseTable
    else:
        print("Get ids ERROR!")
        exit(4)


def parseCourseTable(courseTable):
    """
    解析课表
    :param courseTable: {Response} 课表html响应
    :return:
    """
    soup = BeautifulSoup(courseTable.text.encode('utf-8'), 'lxml')

    """personal info"""
    personalInfo = soup.select('div#ExportA > div')[0].get_text()
    # print(personalInfo)  # DEBUG
    stuClass = re.findall(r'所属班级:\s*([A-Za-z\d]*)', personalInfo)[0]
    print('班级:' + stuClass)
    practiceWeek = re.findall(r'实践周：\s*(.*)', personalInfo, re.DOTALL)[0]
    practiceWeek = "".join(practiceWeek.split())
    print('实践周:' + practiceWeek)

    courseTable_JS = soup.select('div#ExportA > script')[0].get_text()
    # print(courseTable_JS)
    list_courses = courseTable_JS.split('var teachers =')

    """Regex"""
    re_teachers = re.compile(r'actTeachers\s*=\s*\[(.+)];')
    re_singleTeacher = re.compile(r'({.+?})')
    re_courseInfo = re.compile(
        r'actTeacherName\.join\(\',\'\),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*)\s*\)')
    # courseId,courseName,roomId,roomName,vaildWeeks,taskId,remark,assistantName,experiItemName,schGroupNo
    re_courseTime = re.compile(r'index\s*=\s*(\d+)\s*\*\s*unitCount\s*\+\s*(\d+);')

    course_cnt = 1
    for singleCourse in list_courses[1:]:
        print('No.{} course: '.format(course_cnt))
        list_teacher = []
        teachers = re_teachers.findall(singleCourse)
        # print(teachers)
        # print('Parsing teacher(s)...')  # DEBUG
        teacher = re_singleTeacher.findall(teachers[0])
        if len(teacher) > 1:  # More than 1 teachers
            for teacher_i in teacher:
                teacher_i = teacher_i.replace('id', '\"id\"').replace('name', '\"name\"').replace('lab', '\"lab\"')
                list_teacher.append(json.loads(teacher_i))
        else:  # Single teacher
            teacher = teacher[0].replace('id', '\"id\"').replace('name', '\"name\"').replace('lab', '\"lab\"')
            list_teacher.append(json.loads(teacher))
        # print(list_teacher)
        print([list_teacher[i]['name'] for i in range(len(list_teacher))])

        # print('Parsing course info...')  # DEBUG
        courseInfo = re_courseInfo.search(singleCourse, re.DOTALL | re.MULTILINE)
        # print(courseInfo)
        courseName = re.sub(r'<sup .*?>', '', courseInfo[2]).replace('</sup>', '')  # 去除sup标签
        print(courseName)  # courseName
        print(courseInfo[4])  # roomName
        print(courseInfo[5])  # vaildWeeks

        # print('Parsing course time...')  # DEBUG
        courseTime = re_courseTime.findall(singleCourse)
        # print(courseTime)
        day_of_week = str(int(courseTime[0][0]) + 1)
        course_unit = ','.join([str(int(courseTime[i][1]) + 1) for i in range(len(courseTime))])
        print("星期" + {
            '1': '一',
            '2': '二',
            '3': '三',
            '4': '四',
            '5': '五',
            '6': '六',
            '7': '日',
        }.get(day_of_week) + " 第" + course_unit + "节")

        course_cnt += 1
        print()


if __name__ == "__main__":
    # 学号及密码
    stuID = r""
    stuPwd = r""
    retry_cnt = 3  # 登录重试次数

    temp_time = time.time()
    try:
        name = aao_login(stuID, stuPwd, retry_cnt)
        print('\nMiao~下面开始获取课表啦！\n')
        courseTable = getCourseTable(choice=0)
        parseCourseTable(courseTable)
    except Exception as e:
        print("ERROR!")
        print(e)
    print('累计用时：', time.time() - temp_time, 's')
