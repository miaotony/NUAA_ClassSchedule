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
            batch1_tmh = ('T11', 'T12', 'T13')
            batch2_tmh = ('T14', 'T15')

            # Lesson start time
            # 潜在bug: roomName为空的情况默认为将军路明故宫的时间表
            if '天目湖' in lesson.roomName:
                if lesson.roomName.startswith(batch1_tmh):
                    course_order = {
                        '1': "08:30",
                        '2': "09:25",
                        '3': "10:25",
                        '4': "11:20",
                        '5': "14:00",
                        '6': "14:55",
                        '7': "16:00",
                        '8': "16:55",
                        '9': "18:45",
                        '10': "19:40",
                        '11': "20:35",
                    }
                    end_time = {
                        '1': "09:20",
                        '2': "10:15",
                        '3': "11:15",
                        '4': "12:10",
                        '5': "14:50",
                        '6': "15:45",
                        '7': "16:50",
                        '8': "17:45",
                        '9': "19:35",
                        '10': "20:30",
                        '11': "21:25",
                    }
                elif lesson.roomName.startswith(batch2_tmh):
                    course_order = {
                        '1': "08:30",
                        '2': "09:25",
                        '3': "10:40",
                        '4': "11:35",
                        '5': "14:00",
                        '6': "14:55",
                        '7': "16:00",
                        '8': "16:55",
                        '9': "18:45",
                        '10': "19:40",
                        '11': "20:35",
                    }
                    end_time = {
                        '1': "09:20",
                        '2': "10:15",
                        '3': "11:30",
                        '4': "12:25",
                        '5': "14:50",
                        '6': "15:45",
                        '7': "16:50",
                        '8': "17:45",
                        '9': "19:35",
                        '10': "20:30",
                        '11': "21:25",
                    }
                else:
                    course_order = {
                        '1': "08:30",
                        '2': "09:25",
                        '3': "10:30",
                        '4': "11:25",
                        '5': "14:00",
                        '6': "14:55",
                        '7': "16:00",
                        '8': "16:55",
                        '9': "18:45",
                        '10': "19:40",
                        '11': "20:35",
                    }
                    end_time = {
                        '1': "09:20",
                        '2': "10:15",
                        '3': "11:20",
                        '4': "12:15",
                        '5': "14:50",
                        '6': "15:45",
                        '7': "16:50",
                        '8': "17:45",
                        '9': "19:35",
                        '10': "20:30",
                        '11': "21:25",
                    }
            elif ('明故宫' in lesson.roomName and lesson.roomName.startswith(batch1_mgg)) or \
                    ('将军路' in lesson.roomName and lesson.roomName.startswith(batch1_jjl)):
                # Batch 1
                course_order = {
                    '1': "08:00",
                    '2': "08:55",
                    '3': "10:05",
                    '4': "11:00",
                    '5': "14:00",
                    '6': "14:55",
                    '7': "16:15",
                    '8': "17:10",
                    '9': "18:45",
                    '10': "19:40",
                    '11': "20:35",
                }
                end_time = {
                    '1': "08:50",
                    '2': "09:45",
                    '3': "10:55",
                    '4': "11:50",
                    '5': "14:50",
                    '6': "15:45",
                    '7': "17:05",
                    '8': "18:00",
                    '9': "19:35",
                    '10': "20:30",
                    '11': "21:25",
                }
            elif ('明故宫' in lesson.roomName and lesson.roomName.startswith(batch2_mgg)) or \
                    ('将军路' in lesson.roomName and lesson.roomName.startswith(batch2_jjl)):
                # Batch 2
                course_order = {
                    '1': "08:00",
                    '2': "08:55",
                    '3': "10:25",
                    '4': "11:20",
                    '5': "14:00",
                    '6': "14:55",
                    '7': "16:15",
                    '8': "17:10",
                    '9': "18:45",
                    '10': "19:40",
                    '11': "20:35",
                }
                end_time = {
                    '1': "8:50",
                    '2': "9:45",
                    '3': "11:15",
                    '4': "12:10",
                    '5': "14:50",
                    '6': "15:45",
                    '7': "17:05",
                    '8': "18:00",
                    '9': "19:35",
                    '10': "20:30",
                    '11': "21:25",
                }
            else:
                course_order = {
                    '1': "08:00",
                    '2': "08:55",
                    '3': "10:15",
                    '4': "11:10",
                    '5': "14:00",
                    '6': "14:55",
                    '7': "16:15",
                    '8': "17:10",
                    '9': "18:45",
                    '10': "19:40",
                    '11': "20:35",
                }
                end_time = {
                    '1': "08:50",
                    '2': "09:45",
                    '3': "11:05",
                    '4': "12:00",
                    '5': "14:50",
                    '6': "15:45",
                    '7': "17:05",
                    '8': "18:00",
                    '9': "19:35",
                    '10': "20:30",
                    '11': "21:25",
                }

            lesson_start = course_order[lesson.course_unit[0]].split(":")
            lesson_start_hour = int(lesson_start[0])
            lesson_start_minute = int(lesson_start[1])
            lesson_start_time = semester_start_date + \
                timedelta(weeks=week - 1, days=int(lesson.day_of_week) - 1,
                          hours=lesson_start_hour - semester_start_date.hour,
                          minutes=lesson_start_minute - semester_start_date.minute,
                          seconds=-semester_start_date.second,
                          milliseconds=-semester_start_date.microsecond)

            elapsed_time = datetime.strptime(end_time[lesson.course_unit[len(lesson.course_unit) - 1]], "%H:%M") - \
                datetime.strptime(course_order[lesson.course_unit[0]], "%H:%M")
            lesson_end_time = lesson_start_time + \
                timedelta(minutes=(elapsed_time / 60).seconds)

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


def create_weeknum_ics(cal, semester_start_date):
    """
    给ical生成周数事件（持续一周的`第x周`事件）
    :param cal: 加入了课表后的cal
    :param semester_start_date: {datatime}学期开始日期):
    :return: cal {Calendar}
    """
    for week_num in range(1, 21):
        # 20 weeks
        event = Event()
        event.add('summary', '第 ' + str(week_num) + ' 周')
        weekStartTime = semester_start_date + \
            timedelta(weeks=week_num - 1, days=0, hours=0,
                      minutes=0, seconds=0, milliseconds=0)

        weekEndTime = semester_start_date + \
            timedelta(weeks=week_num - 1, days=7, hours=0,
                      minutes=0, seconds=0, milliseconds=0)
        event.add('dtstart', weekStartTime)
        event.add('dtend', weekEndTime)
        event.add('location', 'NUAA')
        event.add('description', '第 ' + str(week_num) + ' 周')
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
