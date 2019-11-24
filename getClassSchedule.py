#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
getClassSchedule  登录教务系统，获取课表，进行解析及导出

@Author: MiaoTony
"""

import requests
import re
from bs4 import BeautifulSoup
from hashlib import sha1
import time
import random
import json
import logging
import tkinter as tk
import tkinter.ttk
from PIL import Image, ImageTk
from io import BytesIO
# from pytesseract import image_to_string
from lessonObj import Lesson
from examObj import Exam

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


def aao_login(stuID, stuPwd, captcha_str, retry_cnt=1):
    """
    登录新教务系统
    :param stuID: 学号
    :param stuPwd: 密码
    :param retry_cnt: 登录重试次数
    :return: name: {str} 姓名(学号)
    """
    try_cnt = 1
    while try_cnt <= retry_cnt:
        # session.cookies.clear()  # 先清一下cookie
        r1 = session.get(host + '/eams/login.action')
        # logging.debug(r1.text)
        # captcha_resp = session.get(host + '/eams/captcha/image.action')  # Captcha 验证码图片

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

            # Captcha 验证码 # Fix Issue #13 bug, but only for Windows.
            # captcha_img = Image.open(BytesIO(captcha_resp.content))
            # captcha_img.show()  # show the captcha

            # img= ImageTk.PhotoImage(captcha_img)
            # label_img = tkinter.ttk.Label(window, image = img).place(x = 560, y = 2)

            # text = image_to_string(captcha_img)  # 前提是装了Tesseract-OCR，可以试试自动识别
            # print(text)
            # captcha_str = input('Please input the captcha:')

            # 开始登录啦
            postData = {'username': stuID, 'password': postPwd, 'captcha_response': captcha_str}
            time.sleep(0.5 * try_cnt)  # fix Issue #2 `Too Quick Click` bug, sleep for longer time for a new trial
            r2 = session.post(host + '/eams/login.action', data=postData)
            if r2.status_code == 200 or r2.status_code == 302:
                logging.debug(r2.text)
                temp_key = temp_token_match.search(r2.text)
                if temp_key:  # 找到密钥说明没有登录成功，需要重试
                    print("ID, Password or Captcha ERROR! Login ERROR!\n")
                    temp_key = temp_key.group(1)
                    logging.debug(temp_key)
                    exit(2)
                elif re.search(r"ui-state-error", r2.text):  # 过快点击
                    print("ERROR! 请不要过快点击!\n")
                    time.sleep(1)
                    try_cnt += 1
                    # session.headers["User-Agent"] = UAs[1]  # random.randint(0, len(UAs)-1)  # 换UA也不行
                    # exit(3)
                else:
                    temp_soup = BeautifulSoup(r2.text.encode('utf-8'), 'lxml')
                    name = temp_soup.find('a', class_='personal-name').string.strip()
                    print("Login OK!\nHello, {}!".format(name))
                    return name
            else:
                print("Login ERROR!\n")
                exit(1)
        else:
            print('Search token ERROR!\n')
            exit(1)
    print("ERROR! 过一会儿再试试吧...\n")
    exit(3)


def getCourseTable(choice=0):
    """
    获取课表
    :param choice: 0 for std, 1 for class.个人课表or班级课表，默认为个人课表。
    :return:courseTable: {Response} 课表html响应
    """
    time.sleep(0.5)  # fix Issue #2 `Too Quick Click` bug
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
    :return: list_lessonObj: {list} 由Lesson类构成的列表
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
        r'actTeacherName\.join\(\',\'\),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*)\s*,\s*(.*)\s*\)')
    # courseId,courseName,roomId,roomName,vaildWeeks,taskId,remark,assistantName,experiItemName,schGroupNo,teachClassName
    re_courseTime = re.compile(r'index\s*=\s*(\d+)\s*\*\s*unitCount\s*\+\s*(\d+);')

    list_lessonObj = []  # Initialization
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

        logging.info('Parsing course info...')  # DEBUG
        courseInfo = re_courseInfo.search(singleCourse, re.DOTALL | re.MULTILINE)
        logging.debug(courseInfo)

        logging.info('Parsing course time...')  # DEBUG
        courseTime = re_courseTime.findall(singleCourse)
        logging.info(courseTime)

        new_lessonObj = Lesson(list_teacher, courseInfo, courseTime)
        # 把课程的全部信息都传给Lesson，在初始化时进行具体信息的匹配，后续有改动直接在Lesson类里面改就完事了
        """Print info"""
        print(new_lessonObj)
        list_lessonObj.append(new_lessonObj)

        course_cnt += 1
        print()
    return list_lessonObj


def getExamSchedule():
    """
    获取考试安排
    :return:Ans_list: {list} 考试安排列表
    """
    time.sleep(0.5)
    examSchedule = session.get(host + r'/eams/examSearchForStd!examTable.action')

    soup = BeautifulSoup(examSchedule.text.encode('utf-8'), 'lxml')
    '''exam Schedule'''
    exam_Schedule_Text = soup.select('tbody > tr')
    # print(exam_Schedule_Text)
    Ans_list = []
    for single_exam_Schedule in exam_Schedule_Text:
        tmp = []
        single_exam_Schedule = single_exam_Schedule.find_all('td')
        for i in single_exam_Schedule:
            tmp.append(i.get_text().strip())
        Ans_list.append(tmp)
    return Ans_list


def parseExamSchedule(exams):
    '''
    解析考试列表
    :return: examObj
    '''
    list_examObj = []
    if len(exams) > 0:
        for exam in exams:
            temp_ExamObj = Exam(exam)
            print(temp_ExamObj.str_for_print)  # print the exam info
            list_examObj.append(Exam(exam))
    else:
        print('暂无考试安排！')
    return list_examObj
    # return map(Exam,exams)


def exportCourseTable(list_lessonObj, list_examObj, semester_year, semester, stuID):
    """
    导出课表到文件
    :param list_lessonObj: {list}Lesson类组成的列表，包含所有课表信息
    :param list_examObj: {list}Exam类组成的列表，包含考试信息
    :param semester_year: {str}学年
    :param semester: {str}学期 '1'或'2'
    :param stuID {str}学号
    :return: None
    """
    filename = 'NUAAiCal-Data/NUAA-curriculum-' + semester_year + '-' + semester + '-' + stuID + '.txt'
    with open(filename, 'w', encoding='utf-8') as output_file:
        try:
            course_cnt = 1
            for lessonObj in list_lessonObj:
                output_file.write('No.{} course: \n'.format(course_cnt))
                output_file.write(lessonObj.str_for_print)
                output_file.write('\n\n')
                course_cnt += 1
            if len(list_examObj) > 0:
                output_file.write('---------以下为考试信息----------\n')
                for examObj in list_examObj:
                    output_file.write(examObj.str_for_print)
                    output_file.write('\n')
        except Exception as e:
            print('ERROR! 导出课表到文件出错！')
            print(e)
