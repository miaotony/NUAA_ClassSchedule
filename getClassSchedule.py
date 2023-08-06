#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
getClassSchedule  登录教务系统，获取课表，进行解析及导出

@Author: MiaoTony, ZegWe
"""

import requests
import re
from bs4 import BeautifulSoup
from hashlib import sha1
import time
import random
import json
import demjson3
import logging
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
host = r'https://aao-eas.nuaa.edu.cn'


def getSemesterFirstDay(semester_str: str):
    """
    从教务系统校历获取学期的第一天
    :param semester_str: 查询所需的学期字符串 e.g.`2020-2021-1`
    :return semester_year: {str} 学年
    :return semester: {str} 学期
    :return year, month, day: {int} 开学日期
    """
    # 先来判断一下输入字符串的有效性
    re_semester = re.compile(r'[0-9]{4}-[0-9]{4}-[1-2]')
    if not re_semester.findall(semester_str):
        raise Exception('Parse semester ERROR!')
    # 再来解析学期字符串
    years = semester_str.split('-')[0:2]
    term = int(semester_str.split('-')[2])
    # print(years, term)
    requestData = {'schoolYear': '-'.join(years),
                   'term': term}
    r = session.post(host + '/eams/calendarView!search.action',
                     requestData, timeout=10)
    if re.search(r'当前学期不存在', r.text) != None:
        raise Exception('ERROR! The current semester does not exist!')
    # print(r.text)
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    monthstr = soup.select('table > tr')[0].select('td')[1].get_text().replace(
        ' ', '').replace('\r', '').replace('\n', '')
    daystr = soup.select('table > tr')[2].select('td')[1].get_text().replace(
        ' ', '').replace('\r', '').replace('\n', '')
    months = dict(一=1, 二=2, 三=3, 四=4, 五=5, 六=6,
                  七=7, 八=8, 九=9, 十=10, 十一=11, 十二=12)
    year = int(years[term - 1])
    month = months[monthstr]
    day = int(daystr)
    semester_year = '-'.join(years)
    semester = str(term)
    return semester_year, semester, year, month, day


def aao_login(stuID, stuPwd, captcha_str):
    """
    登录新教务系统
    :param stuID: 学号
    :param stuPwd: 密码
    :param captcha_str: 验证码
    :return name: {str} 姓名(学号)
    :return semester_info: {str} 学期信息，如 `2020-2021-1`
    """
    # session.cookies.clear()  # 先清一下cookie
    r1 = session.get(host + '/eams/login.action', timeout=10)
    r1.encoding = 'utf-8'
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
        postData = {'captcha': captcha_str,
                    'username': stuID, 'password': postPwd}
        # fix Issue #2 `Too Quick Click` bug, sleep for longer time for a new trial
        time.sleep(random.uniform(0.7, 1))  # 更改为随机延时
        r2 = session.post(host + '/eams/login!sendPhoneCaptcha.action',
                          data=postData, timeout=10)

        print("请等待短信验证码，或者在微信我的消息栏目中的验证码，并输入：")
        captcha_phone = input()

        # 开始登录啦
        postData = {'ekingstar': 2, 'username': stuID, 'password': postPwd,
                    'captcha_response': captcha_str, 'captcha_phone': captcha_phone}
        time.sleep(random.uniform(0.7, 1))  # 更改为随机延时
        r2 = session.post(host + '/eams/login.action',
                          data=postData, timeout=10)
        r2.encoding = 'utf-8'
        if r2.status_code == 200 or r2.status_code == 302:
            logging.debug(r2.text)
            temp_key = temp_token_match.search(r2.text)
            if temp_key:  # 找到密钥说明没有登录成功，需要重试
                if '验证码不正确' in r2.text:
                    raise Exception("Captcha ERROR! Login ERROR!")
                else:
                    temp_key = temp_key.group(1)
                    logging.debug(temp_key)
                    raise Exception("ID or Password ERROR! Login ERROR!")
            elif re.search(r"ui-state-error", r2.text):  # 过快点击
                raise Exception("ERROR! 请不要过快点击!")
            else:
                temp_soup = BeautifulSoup(r2.text.encode('utf-8'), 'lxml')
                # 提取姓名
                name = temp_soup.find(
                    'a', class_='personal-name').string.strip()
                # 提取当前学期信息
                semester_info_raw = temp_soup.select(
                    '#teach-week')[0].text.strip()
                # print(semester_info_raw)
                re_semesterInfo = re.compile(r'(\d{4}-\d{4})第(\d{1})学期')
                semester_info = re_semesterInfo.search(semester_info_raw)
                semester_info = semester_info[1] + '-' + semester_info[2]
                print("Login OK!\nHello, {}!".format(name))
                print("The current semester is {}.".format(semester_info))
                return name, semester_info
        else:
            print(r2.text)
            if '连接已重置' in r2.text:
                raise Exception("Login ERROR! 教务系统连接已重置，请重试！")
            else:
                raise Exception("Login ERROR!")
    else:
        raise Exception("Search token ERROR!")


def getCourseTable2(stuID, choice=0, semester_year="", semester=""):
    """
    获取课表
    :param stuID: 学号
    :param choice: 0 for std, 1 for class.个人课表or班级课表，默认为个人课表。
    :param semester_year: `xxxx-xxxx` 学年 e.g. `2020-2021`
    :param semester: `x` 学期 {1, 2}
    :return:courseTable: {Response} 课表html响应
    """
    # fix Issue #2 `Too Quick Click` bug
    time.sleep(random.uniform(0.6, 1))  # 随机延时
    semesterCalendar = session.get(
        host + '/eams/dataQuery.action?dataType=semesterCalendar', timeout=10)
    # print(semesterCalendar.text)
    calendar = '{' + \
               re.compile(r'semesters:.*}').findall(semesterCalendar.text)[0]
    # print(calendar)
    calendar = demjson3.decode(calendar)['semesters']

    semester_id = ''
    for y in calendar:
        for s in calendar[y]:
            if s['schoolYear'] == semester_year and s['name'] == str(semester):
                semester_id = s['id']
                break
    # print(semester_id)
    if not semester_id:
        raise Exception("Can not find the semester you have entered!")

    # query the `ids` / get the course table url using stuID
    query_payload = {
        "std.code": stuID,
        "semester.id": semester_id,
        "courseTableType": "std"
    }
    query_response = session.post(
        host + '/eams/courseTableStudent!search.action', params=query_payload, timeout=10)
    query_response.encoding = 'utf-8'
    soup = BeautifulSoup(query_response.text, 'lxml')
    tr = soup.select(".gridtable tbody tr")
    courseTable_url = ""
    for row in tr:
        # process multiple student ids
        stdCode = row.select('td.stdCode')[0]
        stdCode = stdCode.text.strip()
        if stdCode == stuID:
            courseTable_url = row.select('td.stdName a')[0].get('href')
            logging.debug(courseTable_url)
    if not courseTable_url:
        raise Exception("Can not find the course table url!")

        # temp_ids_match = re.compile(
        #     r"bg\.form\.addInput\(form,\"ids\",\"([0-9]*)\"")
        # temp_ids = temp_ids_match.findall(courseTableResponse.text)
        # if temp_ids:
        #     logging.debug(temp_ids)  # [0] for std, [1] for class.
        #
        #     # postData_course = {
        #     #     "ignoreHead": "1",
        #     #     "setting.kind": "std",
        #     #     "startWeek": "",
        #     #     "project.id": "1",
        #     #     "semester.id": "62",
        #     #     "ids": "xxxxx"
        #     # }
        #
        #     if choice == 1:  # 班级课表
        #         ids = temp_ids[1]
        #         kind = "class"
        #     else:  # 个人课表   choice == 0
        #         ids = temp_ids[0]
        #         kind = "std"

        # courseTable_postData = {
        #     # "ignoreHead": "1",
        #     "setting.kind": kind,
        #     # "startWeek": "",  # None for all weeks
        #     # "project.id": "1",
        #     "semester.id": semester_id,
        #     "ids": ids
        # }
        # courseTable = session.get(host + r'/eams/courseTableStudent!courseTable.action',
        #                           params=courseTable_postData)

    courseTable = session.get(host + courseTable_url, timeout=10)
    # logging.debug(courseTable.text)
    # logging.debug(session.cookies.get_dict())
    return courseTable


def getCourseTable(stuID, choice=0, semester_year="", semester=""):
    """
    获取课表
    :param stuID: 学号
    :param choice: 0 for std, 1 for class.个人课表or班级课表，默认为个人课表。
    :param semester_year: `xxxx-xxxx` 学年 e.g. `2020-2021`
    :param semester: `x` 学期 {1, 2}
    :return:courseTable: {Response} 课表html响应
    """
    # fix Issue #2 `Too Quick Click` bug
    time.sleep(random.uniform(0.6, 1))  # 随机延时
    semesterCalendar = session.get(
        host + '/eams/dataQuery.action?dataType=semesterCalendar', timeout=10)
    # print(semesterCalendar.text)
    calendar = '{' + \
               re.compile(r'semesters:.*}').findall(semesterCalendar.text)[0]
    # print(calendar)
    calendar = demjson3.decode(calendar)['semesters']

    semester_id = ''
    for y in calendar:
        for s in calendar[y]:
            if s['schoolYear'] == semester_year and s['name'] == str(semester):
                semester_id = s['id']
                break
    # print(semester_id)
    if not semester_id:
        raise Exception("Can not find the semester you have entered!")

    courseTableResponse = session.get(
        host + '/eams/courseTableForStd.action', timeout=10)
    # logging.debug(courseTableResponse.text)

    temp_ids_match = re.compile(
        r"bg\.form\.addInput\(form,\"ids\",\"([0-9]*)\"")
    temp_ids = temp_ids_match.findall(courseTableResponse.text)
    if temp_ids:
        logging.debug(temp_ids)  # [0] for std, [1] for class.

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
            "semester.id": semester_id,
            "ids": ids
        }
        courseTable = session.get(host + r'/eams/courseTableForStd!courseTable.action',
                                  params=courseTable_postData, timeout=10)
        return courseTable
    else:
        raise Exception("Get ids ERROR!")


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
    # 个人课表为`所属班级`，班级课表为`班级名称`
    stuClass = re.findall(r'(所属班级|班级名称):\s*([A-Za-z\d]*)', personalInfo)[0]
    print('班级:' + stuClass[1])
    practiceWeek = re.findall(r'实践周：\s*(.*)', personalInfo, re.DOTALL)[0]
    practiceWeek = "".join(practiceWeek.split())
    print('实践周:' + practiceWeek)

    courseTable_JS = soup.select('div#ExportA > script')[0].decode()
    # logging.debug(courseTable_JS)
    list_courses = courseTable_JS.split('var teachers =')

    """Regex"""
    re_teachers = re.compile(r'actTeachers\s*=\s*\[(.+)];')
    re_singleTeacher = re.compile(r'({.+?})')
    re_courseInfo = re.compile(
        r'actTeacherName\.join\(\',\'\),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*),\s*(.*)\s*,\s*(.*)\s*\)')
    # courseId,courseName,roomId,roomName,vaildWeeks,taskId,remark,assistantName,experiItemName,schGroupNo,teachClassName
    re_courseTime = re.compile(
        r'index\s*=\s*(\d+)\s*\*\s*unitCount\s*\+\s*(\d+);')

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
                    teacher_i = teacher_i.replace('id', '\"id\"').replace(
                        'name', '\"name\"').replace('lab', '\"lab\"')
                    list_teacher.append(json.loads(teacher_i))
            else:  # Single teacher
                teacher = teacher[0].replace('id', '\"id\"').replace(
                    'name', '\"name\"').replace('lab', '\"lab\"')
                list_teacher.append(json.loads(teacher))
        logging.info(list_teacher)

        logging.info('Parsing course info...')  # DEBUG
        courseInfo = re_courseInfo.search(
            singleCourse, re.DOTALL | re.MULTILINE)
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
    time.sleep(random.uniform(0.6, 1))  # 随机延时
    examSchedule = session.get(
        host + r'/eams/examSearchForStd!examTable.action', timeout=10)

    soup = BeautifulSoup(examSchedule.text.encode('utf-8'), 'lxml')
    '''exam Schedule'''
    exam_Schedule_Text = soup.select('tbody > tr')
    # print(exam_Schedule_Text)
    Ans_list = []

    if exam_Schedule_Text:  # add a protection
        for single_exam_Schedule in exam_Schedule_Text:
            tmp = []
            single_exam_Schedule = single_exam_Schedule.find_all('td')
            if single_exam_Schedule:  # add a protection
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
            print()
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
    filename = 'NUAAiCal-Data/Schedule_' + stuID + \
               '_' + semester_year + '-' + semester + '.txt'
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
