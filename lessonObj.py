#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
lessonObj  课程Lesson类相关属性及方法

@Author: MiaoTony
"""
import re


class Lesson:
    def __init__(self, list_teacher, courseInfo, courseTime):
        """
        Initialization 在初始化同时解析课程的具体信息
        :param list_teacher: 教师信息JSON格式列表
        :param courseInfo: 课程信息列表
        :param courseTime: 课程时间
        """
        # self.list_teacher = list_teacher  # 节约一点内存...
        # self.courseInfo = courseInfo
        # self.courseTime = courseTime

        """下面开始解析具体信息  Parsing From here"""
        self.teacherName = [list_teacher[i]['name'] for i in range(len(list_teacher))]
        self.courseId = courseInfo[1].replace('"', '')
        # 去除sup标签及自带的`"`
        self.courseName = re.sub(r'<sup .*?>', '', courseInfo[2]).replace('</sup>', '').replace('"', '')
        self.roomId = courseInfo[3].replace('"', '')
        self.roomName = courseInfo[4].replace('"', '')
        temp_weeks = courseInfo[5].replace('"', '')
        self.vaildWeeks = [Week_i for Week_i in range(1, len(temp_weeks)) if temp_weeks[Week_i] == '1']  # So cool!
        self.day_of_week = str(int(courseTime[0][0]) + 1)
        self.course_unit = [str(int(courseTime[i][1]) + 1) for i in range(len(courseTime))]

        str_teacherName = ','.join(self.teacherName)
        str_vaildWeeks = ','.join(map(str, self.vaildWeeks))
        str_courseUnit = ','.join(self.course_unit)
        str_courseTime = "星期" + {
            '1': '一',
            '2': '二',
            '3': '三',
            '4': '四',
            '5': '五',
            '6': '六',
            '7': '日',
        }.get(self.day_of_week) + " 第" + str_courseUnit + "节"
        self.str_for_print = '\n'.join(
            [self.courseName, str_teacherName, self.roomName, '第' + str_vaildWeeks + '周', str_courseTime])

    def __str__(self):
        """
        魔法方法输出课程信息
        :return: {str} 课程信息
        """
        return self.str_for_print

    def output_description(self, week):
        """
        输出ics描述
        :param week: {int} 当前周
        :return:description: {str} 合成好的描述字符串
        """
        description = ','.join(self.teacherName) + \
                      " \n当前周次：%d" % week + \
                      " \n上课周次：" + ','.join(map(str, self.vaildWeeks)) + \
                      " \n\nPowered by NUAA_ClassSchedule. \nURL: https://github.com/miaotony/NUAA_ClassSchedule "
        return description
