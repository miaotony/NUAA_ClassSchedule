#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
generateICS  生成及导出.ics日历文件

@Author: MiaoTony, Triple-Z(原作者)
"""

from icalendar import Calendar, Event
from datetime import datetime, timedelta
from pytz import timezone
# import tempfile
from hashlib import md5
import os


# from sys import getsizeof


def create_ics(lessons, semester_start_date):
    """
    生成课表的ical
    :param lessons: {list} Lesson类组成的列表
    :param semester_start_date: {datatime}学期开始日期
    :return: cal {Calendar}
    """
    cal = Calendar()
    cal.add('prodid', '-//miaotony//NUAA_ClassSchedule//CN')
    cal.add('version', '2.0')
    cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')

    for lesson in lessons:
        for week in lesson.vaildWeeks:
            event = Event()
            event.add('summary', lesson.courseName)

            # 错峰时间批次对应的教学楼
            batch1_jjl = ('1', '6', '7', 'D2')  # 将军路校区
            batch1_mgg = ('18',)                # 明故宫校区
            batch2_jjl = ('2', '4', '5', 'D1', 'D3')
            batch2_mgg = ('7', '13')
            batch1_tmh = ('T1', 'T2', 'T3')

            # Lesson start time
# 匹配天目湖校区时间表
# 潜在bug: roomName为空的情况默认为将军路明故宫的时间表
            if '天目湖' in lesson.roomName:
                if lesson.roomName.startswith(batch1_tmh):
                    lesson_start_hour = {
                        '1': 8,
                        '3': 10,
                        '5': 14,
                        '7': 16,
                        '9': 18,
                        '11': 20,
                    }.get(lesson.course_unit[0])
                    lesson_start_minute = {
                        '1': 30,
                        '3': 25,
                        '5': 0,
                        '7': 0,
                        '9': 45,
                        '11': 35,
                    }.get(lesson.course_unit[0])
                else:
                    lesson_start_hour = {
                        '1': 8,
                        '3': 10,
                        '5': 14,
                        '7': 16,
                        '9': 18,
                        '11': 20,
                    }.get(lesson.course_unit[0])
                    lesson_start_minute = {
                        '1': 30,
                        '3': 40,
                        '5': 0,
                        '7': 0,
                        '9': 45,
                        '11': 35,
                    }.get(lesson.course_unit[0])
            elif ('明故宫' in lesson.roomName and lesson.roomName.startswith(batch1_mgg)) or \
                    ('将军路' in lesson.roomName and lesson.roomName.startswith(batch1_jjl)):
                # Batch 1
                lesson_start_hour = {
                    '1': 8,
                    '3': 10,
                    '5': 14,
                    '7': 16,
                    '9': 18,
                    '11': 20,
                }.get(lesson.course_unit[0])
                lesson_start_minute = {
                    '1': 0,
                    '3': 5,  # <--
                    '5': 0,
                    '7': 15,
                    '9': 45,
                    '11': 35,
                }.get(lesson.course_unit[0])
            elif ('明故宫' in lesson.roomName and lesson.roomName.startswith(batch2_mgg)) or \
                    ('将军路' in lesson.roomName and lesson.roomName.startswith(batch2_jjl)):
                # Batch 2
                lesson_start_hour = {
                    '1': 8,
                    '3': 10,
                    '5': 14,
                    '7': 16,
                    '9': 18,
                    '11': 20,
                }.get(lesson.course_unit[0])
                lesson_start_minute = {
                    '1': 0,
                    '3': 25,  # <--
                    '5': 0,
                    '7': 15,
                    '9': 45,
                    '11': 35,
                }.get(lesson.course_unit[0])
            else:
                lesson_start_hour = {
                    '1': 8,
                    '3': 10,
                    '5': 14,
                    '7': 16,
                    '9': 18,
                    '11': 20,
                }.get(lesson.course_unit[0])
                lesson_start_minute = {
                    '1': 0,
                    '3': 15,
                    '5': 0,
                    '7': 15,
                    '9': 45,
                    '11': 35,
                }.get(lesson.course_unit[0])

            lesson_start_time = semester_start_date + \
                timedelta(weeks=week - 1, days=int(lesson.day_of_week) - 1,
                          hours=lesson_start_hour - semester_start_date.hour,
                          minutes=lesson_start_minute - semester_start_date.minute,
                          seconds=-semester_start_date.second,
                          milliseconds=-semester_start_date.microsecond)

            lesson_end_time = lesson_start_time + timedelta(
                minutes=50 * len(lesson.course_unit) + 5 * (len(lesson.course_unit) - 1))
# fix隐含bug：课程时间仅一节或超过两节（非连续两节课）的情况

            event.add('dtstart', lesson_start_time)
            event.add('dtend', lesson_end_time)
# event.add('dtstamp', datetime.now(tz=timezone('Asia/Shanghai')))
            event.add('location', lesson.roomName)
            try:
                event.add('description', lesson.output_description(week=week))
            except UnicodeDecodeError:
                raise Exception("ERROR!")  # 放弃python2.x了
            cal.add_component(event)
    return cal


def create_exam_ics(cal, exams):
    """
    生成考试安排的iCal
    :param cal: 加入了课表后的cal
    :param exams: {list}考试安排Exam类组成的列表
    :return: cal {Calendar}
    """
    for exam in exams:
        if isinstance(exam.examDate, list):  # 如果时间未确定, 不导出
            event = Event()
            event.add('summary', exam.courseName + '_' + exam.examType)
            # exam start time
            examStartTime = datetime(exam.examDate[0], exam.examDate[1], exam.examDate[2], exam.examTime[0],
                                     exam.examTime[1], 0,
                                     tzinfo=timezone('Asia/Shanghai'))  # examTime[0]、examTime[1] 起始时间
            examEndTime = datetime(exam.examDate[0], exam.examDate[1], exam.examDate[2], exam.examTime[2],
                                   exam.examTime[3], 0,
                                   tzinfo=timezone('Asia/Shanghai'))  # examTime[2]、examTime[3] 终止时间
            event.add('dtstart', examStartTime)
            event.add('dtend', examEndTime)
            event.add('location', exam.examLocation)
            event.add('description', exam.description)
            cal.add_component(event)
        return cal


def export_ics(cal, semester_year, semester, stuID):
    filename = 'NUAAiCal-Data/Schedule_' + stuID + \
        '_' + semester_year + '-' + semester + '.ics'

    if os.path.exists('NUAAiCal-Data'):
        # print('Directory exists.')
        if os.path.isfile(filename):
            # File exists, check whether need to be updated.
            tem = open('.temp', 'w+b')
            tem_path = os.path.abspath(tem.name)
            tem.write(cal.to_ical())
            tem_filename = tem.name
            tem.read()  # fix a py2.7 bug...
            tem.close()
            # print(getsizeof(tem.read()))
            is_update = not is_same(tem_path, filename)
            # print("Temp file name is %s, in %s" % (tem_filename, os.path.abspath(tem_filename)))
            os.remove(tem_path)

            if is_update:
                print('有更新的信息！')
                f = open(os.path.join(filename), 'wb')
                f.write(cal.to_ical())
                f.close()
                print("更新的日历文件已导出到 \"" + os.path.abspath(filename) + "\"。")
            else:
                print('没有需要更新的信息！')
                print("原有的日历文件位置为 \"" + os.path.abspath(filename) + "\"。")

        else:
            f = open(os.path.join(filename), 'wb')
            f.write(cal.to_ical())
            f.close()
            print("日历文件已导出到 \"" + os.path.abspath(filename) + "\"。")
    else:
        os.mkdir('NUAAiCal-Data')

        f = open(os.path.join(filename), 'wb')
        f.write(cal.to_ical())
        f.close()
        # print('ICS file has successfully exported to \"' + filename + '\".')
        print("日历文件已导出到 \"" + os.path.abspath(filename) + "\"。")

    return True


def is_same(file1, file2):
    hash1 = md5()
    with open(file1, 'rb') as f1:
        f1_data = f1.read()
    # print(getsizeof(f1_data))
    hash1.update(f1_data)
    md5_1 = hash1.hexdigest()
    # print(f1_data)
    # print(file1.name)
    # print(md5_1)

    hash2 = md5()
    with open(file2, 'rb') as f2:
        f2_data = f2.read()
        # print(getsizeof(f2_data))
    hash2.update(f2_data)
    md5_2 = hash2.hexdigest()
    # print(f2_data)
    # print(f2.name)
    # print(md5_2)

    # print(f1_data == f2_data)

    if md5_1 == md5_2:
        return True
    else:
        return False
