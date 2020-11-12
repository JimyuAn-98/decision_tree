# -*- coding: utf-8 -*-     支持文件中出现中文字符
###################################################################################################################

"""
Created on Mon Oct 26 20:15:02 2020

@author: Huangjiyuan

代码功能描述: （1）读取处理后的数据
            （2）使用传统决策树架构构建决策树

声明：该代码构建决策树失败
"""
###################################################################################################################

import numpy as np
from scipy import signal
import math
import os
import gc   #gc模块提供一个接口给开发者设置垃圾回收的选项
import time
import pandas as pd     #pandas模块用于将数组数据保存到excel表格文件中

class decision_tree_node:
    input = None
    left_tree_node = None
    right_tree_node = None
    leaf_node = None
    node_label = None

    def __init__(self, input:pd.DataFrame) -> None :
        self.input = input
        counts = list(self.input.groupby('label')['label'].value_counts())
        if max(counts) == len(self.input):           
            self.leaf_node = True
            if counts[0] != 0:            
                self.node_label = 0
            elif counts[1] != 0:
                self.node_label = 1
            else: 
                self.node_label = 2
            print(f'叶子节点，节点类别：{self.nodelabel}')
        return
    
    #判断叶子结点的类别
    ###################################################################################################################
    def judge_leaf_node(self):
        counts = list(self.input.groupby('label')['label'].value_counts())
        if max(counts) == len(self.input):           
            self.leaf_node = True
            if counts[0] != 0:            
                self.node_label = 0
            elif counts[1] != 0:
                self.node_label = 1
            elif counts[2] != 0:
                self.node_label = 2
            else :
                self.node_label = None
        print('叶子节点')
        return
    ###################################################################################################################

    #定义计算切分点的函数
    ###################################################################################################################
    def gini_cal(self,input,attr:str):                                     
        gini = np.zeros(((len(input)-1),2))                  #创建用于存储一个属性值的全部基尼系数的矩阵，其中第一列用于存储切分点，第二列用于存储基尼系数
        #print(input)
        inputx = np.array(self.input[['label',attr]])
        #print(inputx)
        inputx = inputx[inputx[:,1].argsort()]
        #print(inputx)
        for i in range(len(inputx)-1):                           #根据输入矩阵的行的数量进行循环
            ave = (inputx[i][1] + inputx[i+1][1])/2           #计算两个数据点之间的平均值
            #print(ave)
            no_0 = no_1 = no_2 = yes_0 = yes_1 = yes_2 = 0      #给定用于存储根据标签分类后的各个情况的数量的变量
            for j in range(len(inputx)):                         #将全部的数据和计算得到的平均值进行比较
                if inputx[j][1] < ave:                         #如果该数据对应的属性值小于平均值
                    if inputx[j][0] == 0.:                       #如果该数据的标签为0
                        no_0 = no_0 + 1                         #那么no_0+1
                    elif inputx[j][0] == 1.:                     #如果该数据的标签为1
                        no_1 = no_1 + 1                         #那么no_1+1
                    else:                                       #否则
                        no_2 = no_2 + 1                         #no_2+1
                else:
                    if inputx[j][0] == 0.:
                        yes_0 = yes_0 + 1
                    elif inputx[j][0] == 1.:
                        yes_1 = yes_1 + 1
                    else:
                        yes_2 = yes_2 + 1
            s1 = no_0 + no_1 + no_2
            s2 = yes_0 + yes_1 + yes_2
            s = s1 + s2      
            #print(s)
            gini_coe_1 = 1 - (no_0/s)**2 - (no_1/s)**2 - (no_2/s)**2 #基尼系数的算法
            #print(gini_coe_1)
            gini_coe_2 = 1 - (yes_0/s)**2 - (yes_1/s)**2 - (yes_2/s)**2
            #print(gini_coe_2)
            gini_coe = ((s1/s)*gini_coe_1) + ((s2/s)*gini_coe_2)
            gini[i][0] = ave                                    #将计算得到的平均值存储到gini矩阵中的第i行，第一列
            gini[i][1] = gini_coe                               #将计算得到基尼系数存储到gini矩阵中的第i行，第二列
        #print(gini)
        gini_min = gini[gini[:,1].argsort()]                    #将gini矩阵根据第二列，也就是基尼系数，从小到大进行排序，基尼系数最小的矩阵排在第一行
        #print(gini_min)
        return gini_min[0][0]                                   #返回切分点的数值
    ###################################################################################################################

    #划分左右子树
    ###################################################################################################################
    def divide_data(self,attr_temp):
        left_tree = pd.DataFrame()
        right_tree = pd.DataFrame()
        divide_value = self.gini_cal(self.input,attr_temp)
        inputx = np.array(self.input[attr_temp])
        #print(inputx)
        for i in range(len(inputx)):
            if inputx[0] < divide_value:
                left_tree = pd.concat([left_tree,self.input[i:i+1]],ignore_index=True)
            else:
                #print(self.input[i:i+1])
                right_tree = pd.concat([right_tree,self.input[i:i+1]],ignore_index=True)
        if len(left_tree) != 0:
            self.left_tree_node = decision_tree_node(left_tree)
        if len(right_tree) != 0:
            self.right_tree_node = decision_tree_node(right_tree)
        return divide_value,len(left_tree),len(right_tree)
    ###################################################################################################################

def TreeGrowth(node:decision_tree_node,attr:list):
    if node.leaf_node == True:
        return
    
    if len(attr) == 0:
        node.judge_leaf_node()
        return
    
    attr_temp = attr.pop()
    #print(attr_temp)
    floor = 7 - len(attr)

    divide_value, left, right = node.divide_data(attr_temp)
    print(f'第{floor}层，属性：{attr_temp}，本节点划分点：{divide_value}',left,right)
    if left != 0:
        print(f'第{floor}层的左子树：')
        TreeGrowth(node.left_tree_node, attr=attr)
    if right != 0:
        print(f'第{floor}层的右子树：')
        TreeGrowth(node.right_tree_node, attr=attr)


#读取文件并将两个文件合并
###################################################################################################################
columns_name = ['mean','var','dwt_appro','dwt_detail','sampen','hurst','pfd']

dt113 = pd.read_excel(r'result_%d.xlsx'% (113))         #设立data列表变量，python 文件流，%d处，十进制替换为e值，.read读文件
dt113 = dt113.iloc[:,1:]
dt113.columns = ['label','mean','var','dwt_appro','dwt_detail','sampen','hurst','pfd']

dt114 = pd.read_excel(r'result_%d.xlsx'% (114))         #设立data列表变量，python 文件流，%d处，十进制替换为e值，.read读文件
dt114 = dt114.iloc[:,1:]
dt114.columns = ['label','mean','var','dwt_appro','dwt_detail','sampen','hurst','pfd']

dt = pd.concat([dt113,dt114],axis=0,ignore_index=True)
#print(dt)
###################################################################################################################
#dt = dt.drop([''])

node = decision_tree_node(input=dt)
TreeGrowth(node = node, attr = columns_name)

