66# -*- coding: utf-8 -*-     支持文件中出现中文字符
###################################################################################################################

"""
Created on Mon Oct 26 20:15:02 2020

@author: Huangjiyuan

代码功能描述: （1）读取处理后的数据
            （2）使用sklearn的决策树模块对数据构建决策树
            （3）对决策树进行拟合度测试
            （4）保存决策树文件并将决策树可视化

"""
###################################################################################################################

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer #特征转换器
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn import tree

#1.读取文件并将两个文件合并
columns_name = ['mean','var','dwt_appro','dwt_detail','sampen','hurst','pfd']               #设置由各个属性组成的矩阵

dt113 = pd.read_excel(r'result_%d.xlsx'% (113))                                             #读取之前处理得到的result_113文件
dt113 = dt113.iloc[:,1:]                                                                    #去除掉第一列，也就是表格中的序列列
dt113.columns = ['label','mean','var','dwt_appro','dwt_detail','sampen','hurst','pfd']      #为每一列添加名称

dt114 = pd.read_excel(r'result_%d.xlsx'% (114))                                             #读取之前处理得到的result_114文件
dt114 = dt114.iloc[:,1:]
dt114.columns = ['label','mean','var','dwt_appro','dwt_detail','sampen','hurst','pfd']

dt = pd.concat([dt113,dt114],axis=0,ignore_index=True)                                      #将两个矩阵合并成一个矩阵

x = dt[columns_name]        #提取要分类的特征
y = dt['label']             #提取输出结果的特征，也就是标签

#2.数据预处理：训练集测试集分割，数据标准化
Xtrain, Xtest, Ytrain, Ytest = train_test_split(x,y,test_size=0.1)                          #将数据分割为训练集和测试集，测试集占比为0.1

#3.使用决策树对测试数据进行类别预测
dtc = DecisionTreeClassifier()              #初始化决策树
dtc.fit(Xtrain,Ytrain)                      #将训练集数据输入决策树，进行拟合
y_predict = dtc.predict(Xtest)              #输入测试集数据，进行预测
print(y_predict)
print(Ytest)

#4.获取结果报告
print('Accracy:',dtc.score(Xtest,Ytest))    #得到测试集的拟合度数值

#5.将生成的决策树保存，并可视化
with open("jueceshu.dot", 'w') as f:        #利用graphviz将生成的决策树可视化
    f = tree.export_graphviz(dtc
                             ,class_names=columns_name
                             ,out_file = f)
