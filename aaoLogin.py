#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
模拟登录NUAA新版教务系统，获取课表，解析后生成iCal日历文件...

@Author: miaotony
@Version: V0.4.0.20191026
@UpdateLog:
    V0.4.0.20191026 增加命令行参数解析，增加控制台输入学号密码（不回显处理），并与初始设置兼容；修复班级课表中教师为空时解析异常bug
    V0.3.1.20191018 增加解析课程所在周并优化课表输出格式，修复班级课表中班级解析bug，引入logging模块记录日志便于debug
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
import json
import logging
import argparse
import getpass

_version_ = "V0.4.0.20191026"

logging.basicConfig(level=logging.WARNING,
                    format='%(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # 设置日志级别及格式


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
    "User-Agent": UAs[0],  # UAs[random.randint(0, len(UAs) - 1)],  # random UA
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
        # logging.debug(r1.text)

        temp_token_match = re.compile(r"CryptoJS\.SHA1\(\'([0-9a-zA-Z\-]*)\'")
        # 搜索密钥
        if temp_token_match.search(r1.text):
            print("Search token OK!")
            temp_token = temp_token_match.search(r1.text).group(1)
            logging.debug(temp_token)
            postPwd = temp_token + stuPwd
            # logging.debug(postPwd)

            # 开始进行SHA1加密
            s1 = sha1()  # 创建sha1对象
            s1.update(postPwd.encode())  # 对s1进行更新
            postPwd = s1.hexdigest()  # 加密处理
            # logging.debug(postPwd)  # 结果是40位字符串

            # 开始登录啦
            # while retry_cnt >= 0:
            postData = {'username': stuID, 'password': postPwd}
            r2 = session.post(host + '/eams/login.action', data=postData)
            if r2.status_code == 200 or r2.status_code == 302:
                logging.debug(r2.text)
                temp_key = temp_token_match.search(r2.text)
                if temp_key:  # 找到密钥说明没有登录成功，需要重试
                    print("ID or Password ERROR! Login ERROR!\n")
                    temp_key = temp_key.group(1)
                    logging.debug(temp_key)
                    exit(2)
                elif re.search(r"ui-state-error", r2.text):  # 过快点击
                    print("ERROR! 请不要过快点击!\n")
                    time.sleep(2)
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
    # logging.debug(courseTableResponse.text)

    temp_ids_match = re.compile(r"bg\.form\.addInput\(form,\"ids\",\"([0-9]*)\"")
    temp_ids = temp_ids_match.findall(courseTableResponse.text)
    if temp_ids:
        logging.debug(temp_ids)  # [0] for std, [1] for class.

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

        # logging.debug(courseTable.text)
        # logging.debug(session.cookies.get_dict())
        return courseTable
    else:
        print("Get ids ERROR!")
        exit(4)


def parseCourseTable(courseTable):
    """
    解析课表
    :param courseTable: {Response} 课表html响应
    :return: None
    """
    soup = BeautifulSoup(courseTable.text.encode('utf-8'), 'lxml')

    """personal info"""
    personalInfo = soup.select('div#ExportA > div')[0].get_text()
    logging.debug(personalInfo)  # DEBUG
    stuClass = re.findall(r'(所属班级|班级名称):\s*([A-Za-z\d]*)', personalInfo)[0]  # 个人课表为`所属班级`，班级课表为`班级名称`
    print('班级:' + stuClass[1])
    practiceWeek = re.findall(r'实践周：\s*(.*)', personalInfo, re.DOTALL)[0]
    practiceWeek = "".join(practiceWeek.split())
    print('实践周:' + practiceWeek)

    courseTable_JS = soup.select('div#ExportA > script')[0].get_text()
    # logging.debug(courseTable_JS)
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

        logging.info('Parsing teacher(s)...')
        list_teacher = []
        teachers = re_teachers.findall(singleCourse)
        if len(teachers) == 0:  # fix teacher not specified bug
            list_teacher = []
        else:
            teacher = re_singleTeacher.findall(teachers[0])
            if len(teacher) > 1:  # More than 1 teachers
                for teacher_i in teacher:
                    teacher_i = teacher_i.replace('id', '\"id\"').replace('name', '\"name\"').replace('lab', '\"lab\"')
                    list_teacher.append(json.loads(teacher_i))
            else:  # Single teacher
                teacher = teacher[0].replace('id', '\"id\"').replace('name', '\"name\"').replace('lab', '\"lab\"')
                list_teacher.append(json.loads(teacher))
        logging.info(list_teacher)

        logging.info('Parsing course info...')
        courseInfo = re_courseInfo.search(singleCourse, re.DOTALL | re.MULTILINE)
        logging.debug(courseInfo)
        courseName = re.sub(r'<sup .*?>', '', courseInfo[2]).replace('</sup>', '').replace('"', '')  # 去除sup标签及自带的`"`
        roomName = courseInfo[4].replace('"', '')
        vaildWeeks = courseInfo[5].replace('"', '')

        logging.info('Parsing course time...')  # DEBUG
        courseTime = re_courseTime.findall(singleCourse)
        logging.info(courseTime)

        """Print info"""
        print(','.join([list_teacher[i]['name'] for i in range(len(list_teacher))]))  # teachers
        print(courseName)  # courseName
        print(roomName)  # roomName
        vaildWeeks_str = ','.join(
            [str(Week_i) for Week_i in range(1, len(vaildWeeks)) if vaildWeeks[Week_i] == '1'])  # So cool!
        print('第' + vaildWeeks_str + '周')
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
    choice = 0  # 0 for std, 1 for class.个人课表or班级课表
    retry_cnt = 3  # 登录重试次数

    print("Welcome to use the NUAA_ClassSchedule script.")
    print("Author: MiaoTony\nGitHub: https://github.com/miaotony/NUAA_ClassSchedule")
    print("Version: " + _version_ + '\n')

    # Parse args 命令行参数解析
    parser = argparse.ArgumentParser()
    parser.description = 'Get NUAA class schedule at ease! 一个小jio本，让你获取课表更加便捷而实在~'
    parser.add_argument("-i", "--id", help="Student ID 学号", type=str)
    parser.add_argument("-p", "--pwd", help="Student password 教务处密码", type=str)
    parser.add_argument("-c", "--choice", help="Input `0` for personal curriculum(default), `1` for class curriculum.\
                        输入`0`获取个人课表(无此参数默认为个人课表)，输入`1`获取班级课表", type=int, choices=[0, 1])  # , default=0

    try:
        # 解析优先级高到低：命令行参数->上面的初始设置->控制台输入
        args = parser.parse_args()
        logging.info(args)

        if args.id is not None:  # 命令行参数优先
            stuID = args.id
        if args.pwd is not None:
            stuPwd = args.pwd
        if args.choice is not None:
            choice = args.choice

        if stuID == '' or stuPwd == '':  # 若学号密码为空则在控制台获取
            print('Please login!')
            stuID = input('Please input your student ID:')
            # stuPwd = input('Please input your password:')
            stuPwd = getpass.getpass('Please input your password:(不会回显，输入完成<ENTER>即可)')
            while True:
                choice = int(input('Please input your choice (`0`: personal, `1`: class):'))
                if choice in [0, 1]:
                    break
                else:
                    print('ERROR! Choice shoule be `0` or `1`!')

        temp_time = time.time()  # 计个时看看
        name = aao_login(stuID, stuPwd, retry_cnt)
        print('\nMeow~下面开始获取{}课表啦！\n'.format({0: '个人', 1: '班级'}.get(choice)))
        courseTable = getCourseTable(choice=choice)
        parseCourseTable(courseTable)
        print('累计用时：', time.time() - temp_time, 's')
        print("Thanks for your use!")
    except Exception as e:
        print("ERROR! 欢迎在GitHub上提出issue & Pull Request!")
        print(e)
    finally:
        print()
