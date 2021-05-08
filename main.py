#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Welcome to use the NUAA_ClassSchedule script.
模拟登录NUAA新版教务系统，获取课表及考试信息，解析后生成iCal日历文件...
GitHub: https://github.com/miaotony/NUAA_ClassSchedule
Pull Requests & issues welcome!

main.py  程序入口

@Author: MiaoTony, ZegWe, Cooook, Pinyi Qian
"""

import os
import sys
import subprocess
from platform import system as system_platform
import time
import logging
import argparse
from getpass import getpass
from datetime import datetime, timedelta
from pytz import timezone
# from io import BytesIO
from generateICS import create_ics, export_ics, create_exam_ics, create_weeknum_ics
from getClassSchedule import *
from generateXLSX import *
from settings import VERSION, DEBUG

if DEBUG:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d]-%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')  # 设置日志级别及格式
else:
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d]-%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')  # 设置日志级别及格式

if __name__ == "__main__":
    # 学号及密码
    stuID = r""
    stuPwd = r""
    choice = 0  # 0 for std, 1 for class. 个人课表or班级课表
    # retry_cnt = 3  # 登录重试次数 Deprecated
    semester_str = ""

    print("Welcome to use the NUAA_ClassSchedule script.")
    print("Author: MiaoTony, ZegWe, Cooook, Pinyi Qian\nGitHub: https://github.com/miaotony/NUAA_ClassSchedule  \n")
    print("Version: " + VERSION + '\n')

    # Parse args 命令行参数解析
    parser = argparse.ArgumentParser()
    parser.description = 'Get NUAA class schedule at ease! 一个小jio本，让你获取课表更加便捷而实在~'
    parser.add_argument("-i", "--id", help="Student ID 学号", type=str)
    parser.add_argument("-p", "--pwd", help="Student password 教务处密码", type=str)
    parser.add_argument("-s", "--semester",
                        help="Semester 学期，例如 `2020-2021-1` 即2020-2021学年第1学期")
    parser.add_argument("-c", "--choice", help="Input `0` for personal curriculum(default), `1` for class curriculum.\
                        输入`0`获取个人课表(无此参数默认为个人课表)，输入`1`获取班级课表", type=int, choices=[0, 1])  # , default=0
    parser.add_argument(
        "--noexam", help="Don't export exam schedule. 加入此选项则不导出考试安排", action="store_true")
    parser.add_argument(
        "--weeknum", help="Export week-number events. 加入此选项则导出周次事件", action="store_true")
    parser.add_argument(
        "--notxt", help="Don't export `.txt` file. 加入此选项则不导出`.txt`文件", action="store_true")
    parser.add_argument(
        "--noxlsx", help="Don't export `.xlsx` file. 加入此选项则不导出`.xlsx`表格", action="store_true")

    try:
        # 解析优先级高到低：命令行参数->上面的初始设置->控制台输入
        args = parser.parse_args()
        logging.info(args)

        print('## Start login!')
        if args.id is not None:  # 命令行参数优先
            stuID = args.id
        if args.pwd is not None:
            stuPwd = args.pwd
        if args.choice is not None:
            choice = args.choice
        if args.semester is not None:
            semester_str = args.semester
        if stuID == '' or stuPwd == '':  # 若学号密码为空则在控制台获取
            stuID = input('Please input your student ID: ')
            # stuPwd = input('Please input your password:')
            stuPwd = getpass(
                'Please input your password:(不会回显，输入完成<ENTER>即可) ')

        # Captcha 验证码 # Fix Issue #13 bug.
        captcha_resp = session.get(
            host + '/eams/captcha/image.action')  # Captcha 验证码图片
        img_path = os.path.join(os.getcwd(), 'captcha.jpg')
        with open(img_path, 'wb') as captcha_fp:
            captcha_fp.write(captcha_resp.content)
        try:
            # 在不同平台显示验证码
            if sys.platform.find('darwin') >= 0:
                subprocess.call(['open', img_path])
            elif sys.platform.find('linux') >= 0:
                subprocess.call(['xdg-open', img_path])
            else:
                os.startfile(img_path)
        except:
            from PIL import Image

            # captcha_img = Image.open(BytesIO(captcha_resp.content))
            captcha_img = Image.open(img_path)
            captcha_img.show()  # show the captcha
            captcha_img.close()

        # text = image_to_string(captcha_img)  # 前提是装了Tesseract-OCR，可以试试自动识别
        # print(text)
        captcha_str = input('Please input the captcha: ')
        print()  # 加个空行好看一点

        # 删除验证码图片
        if sys.platform.find('darwin') >= 0:
            os.system("osascript -e 'quit app \"Preview\"'")
        os.remove(img_path)

        # 开始登录
        name, semester_current = aao_login(stuID, stuPwd, captcha_str)
        if semester_str == '':
            # 若之前的参数为空则在控制台获取学期信息
            semester_str = input("""
Please input the semester you want to query, e.g. `2020-2021-1`: (the current semester by default)
请注意格式，`2020-2021-1`即2020-2021学年第1学期，若查询当前学期请直接敲回车\n""")
        if semester_str == '':
            # 若输入仍为空则默认为当前学期
            semester_str = semester_current
        semester_year, semester, year, month, day = getSemesterFirstDay(
            semester_str)
        print('The start date of {} semester is: {}-{}-{}.'.format(semester_str, year, month, day))
        semester_start_date = datetime(year, month, day, 0, 0, 0,
                                       tzinfo=timezone('Asia/Shanghai'))

        print('\n## Meow~下面开始获取{}课表啦！\n'.format(
            {0: '个人', 1: '班级'}.get(choice)))
        temp_time = time.time()  # 计个时看看
        courseTable = getCourseTable(
            choice=choice, stuID=stuID, semester_year=semester_year, semester=semester)
        list_lessonObj = parseCourseTable(courseTable)

        print('## 下面开始获取考试信息啦！\n')
        examSchedule = getExamSchedule()
        list_examObj = parseExamSchedule(examSchedule)

        print('## 信息获取完成，下面开始生成iCal日历文件啦！')
        cal = create_ics(list_lessonObj, semester_start_date)
        if not args.noexam:  # 若命令行参数含`--noexam`则不导出
            cal = create_exam_ics(cal, list_examObj)
        if args.weeknum:  # 若命令行参数含`--weeknum`则导出周次事件
            cal = create_weeknum_ics(cal, semester_start_date)

        print('## 日历生成完成，下面开始导出啦！')
        export_ics(cal, semester_year, semester, stuID)  # Export `.ics` file
        if not args.notxt:  # 若命令行参数含`--notxt`则不导出
            # Export `.txt` file
            exportCourseTable(list_lessonObj, list_examObj,
                              semester_year, semester, stuID)
        if not args.noxlsx:  # 若命令行参数含`--noxlsx`则不导出
            # Export `.xlsx` file
            print('\n## 开始生成xlsx表格文件！ ')
            xlsx = create_xls(list_lessonObj, semester_year, semester, stuID)
            print('## xlsx文件生成完成，开始导出！')
            export_xls(xlsx, semester_year, semester, stuID)
        print('\n## 导出完成，用时：', time.time() - temp_time, 's')
        print("Thanks for your use! 欢迎来GitHub上点个Star呢！")

    except Exception as e:
        print("ERROR! 如果遇到技术问题，欢迎在GitHub上提出issue & Pull Request!")
        print(e)
    finally:
        session.cookies.clear()  # 清一下cookie
        if system_platform() == 'Windows':  # Fix Linux `sh: 1: pause: not found` bug
            os.system('pause')
