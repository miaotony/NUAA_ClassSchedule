#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI

bug:
    stuID未能显示；没有对输入情况进行判断。
"""
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk
import pickle
import requests
import time
from datetime import datetime, timedelta
from pytz import timezone
from PIL import Image, ImageTk
from io import BytesIO
# from getClassSchedule import aao_login, getCourseTable, parseCourseTable, getExamSchedule,
from getClassSchedule import *
from generateICS import create_ics, export_ics, create_exam_ics
from generateXLSX import *

# import subprocess as sub

# 将命令行结果重定向到GUI
# p = sub.Popen('./script', stdout=sub.PIPE, stderr=sub.PIPE)
# CIL_output, CIL_errors = p.communicate()

session.cookies.clear()  # 先清一下cookie

window = tk.Tk()
window.title('NUAA Class Schedule')
window.geometry("800x600")

tk.Label(window, text='学号:', font=('Arial', 12), width=10, height=2, anchor='w').place(x=30, y=20)
tk.Label(window, text='教务密码:', font=('Arial', 12), width=10, height=2, anchor='w').place(x=250, y=20)
tk.Label(window, text='验证码:', font=('Arial', 12), width=10, height=2, anchor='w').place(x=500, y=20)

et_stunum = tk.Entry(window, show=None, font=('Arial', 14), width=14)
et_passwd = tk.Entry(window, show='*', font=('Arial', 14), width=14)
et_ideco = tk.Entry(window, show=None, font=('Arial', 14), width=10)
et_stunum.place(x=80, y=28)
et_passwd.place(x=330, y=28)
et_ideco.place(x=660, y=28)

captcha_resp = session.get(host + '/eams/captcha/image.action')  # Captcha 验证码图片
captcha_img = Image.open(BytesIO(captcha_resp.content))
img = ImageTk.PhotoImage(captcha_img)
label_img = tkinter.ttk.Label(window, image=img).place(x=560, y=22)

# canvas=tk.Canvas(window,bg='green',height=35,width=90)
# ideco_file=tk.PhotoImage(file='')
# ideco=canvas.create_image(image=ideco_file)

start_term_date = ''
stu_ID = ''

# tk.Label(window, text='学期:', font=('Arial', 12), width=10, height=2, anchor='w').place(x=30, y=40)


# tk.Label(window, text='开学日期: ' + start_term_date, font=('Arial', 12), width=30, height=2, anchor='w').place(x=430, y=40)


# def Select_term():
#     print('selected ' + sele_term.get())


# sele_term = tkinter.ttk.Combobox(window)
# sele_term.place(x=80, y=50)

# sele_term['value'] = ('1', '2', '3', '4')
# # sele_term.current(0)
# sele_term.bind("<<ComboboxSelected>>", Select_term)

tk.Label(window, text='课表类型:', font=('Arial', 12), width=10, height=2, anchor='w').place(x=30, y=100)

var_table_type = tk.IntVar()


def Select_TableType():
    print(var_table_type.get())


rb_presonal = tk.Radiobutton(window, text='个人', variable=var_table_type, value=0, command=Select_TableType).place(x=130,
                                                                                                                  y=100)
rb_class = tk.Radiobutton(window, text='班级', variable=var_table_type, value=1, command=Select_TableType).place(x=130,
                                                                                                               y=120)


def insert_log_end(log_data):
    logbox.insert('end', log_data)


logbox = tk.Text(window, width=75, height=10)
logbox.place(x=230, y=300)
# logbox.insert(tk.END, CIL_output)


# def logIn():
#     aao_login(et_stunum.get(), et_passwd.get(), et_ideco.get(), window)
#
#
# log_In = tk.Button(window, text='登录', font=('Arial', 20), width=10, height=1, command=logIn).place(x=280, y=100)

courseTable = []
courseTableObj = []
examSchedule = []
examScheduleObj = []
semester_start_date = datetime(2020, 2, 24, 0, 0, 0,
                               tzinfo=timezone('Asia/Shanghai'))
semester_year = '2019-2020'
semester = '2'


def getSch():
    global courseTable
    global courseTableObj
    global stu_ID

    stu_ID = et_stunum.get()

    if not courseTable:
        aao_login(et_stunum.get(), et_passwd.get(), et_ideco.get())

    courseTable = getCourseTable(var_table_type.get())
    courseTableObj = parseCourseTable(courseTable)

    if output_exam.get() == 1:
        global examSchedule
        global examScheduleObj
        examSchedule = getExamSchedule()
        examScheduleObj = parseExamSchedule(examSchedule)
    print('GetSchdule here')
    insert_log_end('GetSchdule here.\n')


# get_ideco = tk.Button(window, text='获取验证码', font = ('Arial', 10),height=1, width=10, command=getSch).place(x=560,y=2)  # 增加获取验证码按钮
getSchedule = tk.Button(window, text='获取课表', font=('Arial', 20), width=10, height=1, command=getSch).place(x=530, y=100)

output_exam = tk.IntVar()


def Select_outputExam():
    # if output_exam.get() == 1:
    #     global examSchedule
    #     global examScheduleObj
    #     examSchedule = getExamSchedule()
    #     examScheduleObj = parseExamSchedule(examSchedule)
    print('solve select exam here ' + str(output_exam.get()))


btn_exportExam = tk.Checkbutton(window, text='导出考试安排', variable=output_exam, onvalue=1, offvalue=0,
                                command=Select_outputExam)
btn_exportExam.select()
btn_exportExam.place(x=30, y=150)


def outputAs_iCal():
    cal = create_ics(courseTableObj, semester_start_date)
    if output_exam.get() == 1:
        cal = create_exam_ics(cal, examScheduleObj)
    export_ics(cal, semester_year, semester, stu_ID)
    print('OutputAs_iCal here.')
    insert_log_end('OutputAs_iCal here.\n')


bu_outputAs_iCal = tk.Button(window, text='导出iCal日历', font=('Arial', 20), width=10, height=1,
                             command=outputAs_iCal).place(x=30, y=200)


def outputAs_txt():
    exportCourseTable(courseTableObj, examScheduleObj, semester_year, semester, stu_ID)  # Export `.txt` file
    print('OutputAs_txt here.')
    insert_log_end('OutputAs_txt here.\n')


bu_outputAs_txt = tk.Button(window, text='导出.txt文件', font=('Arial', 20), width=10, height=1,
                            command=outputAs_txt).place(x=280, y=200)


def outputAs_xlsx():
    xlsx = create_xls(courseTableObj, semester_year, semester, stu_ID)
    export_xls(xlsx, semester_year, semester, stu_ID)  # Export `.xlsx` file
    print('OutputAs_xlsx here.')
    insert_log_end('OutputAs_xlsx here.\n')


bu_outputAs_xlsx = tk.Button(window, text='导出.xlsx表格', font=('Arial', 20), width=10, height=1,
                             command=outputAs_xlsx).place(x=530, y=200)


def outputAs_all():
    getSch()
    outputAs_iCal()
    outputAs_txt()
    outputAs_xlsx()
    print('OutputAs_all here.')
    insert_log_end('OutputAs_all here.\n')


bu_outputAs_all = tk.Button(window, text='一键导出', bg='#ffff9f', font=('Arial', 20), width=10, height=1,
                            command=outputAs_all).place(x=30, y=300)

window.mainloop()
