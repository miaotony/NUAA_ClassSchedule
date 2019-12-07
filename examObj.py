#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
examObj  考试Exam类相关属性及方法

@Author: Cooook, Miaotony
"""
import re


class Exam:
    def __init__(self, exam):
        """
        Initialization 在初始化同时解析考试的具体信息
        :param exam: 考试信息列表
        """
        self.courseName = exam[1]
        self.examType = exam[2]
        self.examLocation = exam[5]
        self.examStatue = exam[7]
        self.others = exam[8]
        temp = re.findall(r'(\d*)-(\d*)-(\d*)', exam[3])
        if temp:  # Fix issue #14 `list index out of range`
            list_inter = list(temp[0])
        else:
            list_inter = []

        if not list_inter:
            self.examDate = exam[3]  # 没有的话是字符串直接赋值
            self.examTime = exam[4]
        else:
            self.examDate = list_inter
            list_inter = re.findall(r'(\d*):(\d*)~(\d*):(\d*)', exam[4])
            self.examTime = list(list_inter[0])
            self.examDate = list(map(int, self.examDate))
            self.examTime = list(map(int, self.examTime))

        self.description = '状态：' + self.examStatue + '\n' + self.others
        self.str_for_print = self.courseName + '_' + self.examType + '\n' + exam[3] + ' ' + exam[4] \
                             + '\n' + self.examLocation + '\n' + self.description
