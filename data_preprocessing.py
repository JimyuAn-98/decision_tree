# -*- coding: utf-8 -*-     支持文件中出现中文字符
###################################################################################################################

"""
Created on Sun Oct 18 20:15:02 2020

@author: Huangjiyuan

代码功能描述: （1）读取Sharp_waves文件，
            （2）采用巴特沃斯滤波器，进行60-240Hz滤波
            （3）为数据添加六种属性值，并贴上标签
            （4）将所有属性值组以及标签合成数组并保存在xlsx文件中

"""
###################################################################################################################

import numpy as np
from scipy import signal
import math
import os
import gc   #gc模块提供一个接口给开发者设置垃圾回收的选项
import time
import pandas as pd     #pandas模块用于将数组数据保存到excel表格文件中
import pywt             #pywt模块用于进行小波变换的计算
import pywt.data
from sampen import sampen2      #sampen模块用于进行样本熵的计算
from pyeeg import *             #pyeeg模块用于进行赫斯特指数和Petrosian分形维数的计算

#定义保存数组为xlsx文件的函数
###################################################################################################################
def save_in_xlsx(a,name):                               #函数有两个输入，分别是数据和文件名
    data = pd.DataFrame(a)                              #将数据用DataFrame处理
    writer = pd.ExcelWriter(r'%s.xlsx'%(name))          #创建xlsx文件
    data.to_excel(writer,'page_1',float_format='%.10f') #将数据写入到刚才创建的xlsx文件中
    writer.save()                                       #保存文件
    writer.close()
###################################################################################################################

#读取文件第一列，保存在s1列表中
###################################################################################################################
start = 113 #从start开始做N个文件的图                      #设立变量start，作为循环读取文件的起始
N = 2                                                   #设立变量N，作为循环读取文件的增量
name = 113                                              #文件名
for e in range(start,start+N):                          #循环2次，读取113&114两个文件
    data = open(r'20151026_%d'% (e)).read()             #设立data列表变量，python 文件流，%d处，十进制替换为e值，.read读文件
    data = data.split( )                                #以空格为分隔符，返回数值列表data
    data = [float(s) for s in data]                     #将列表data中的数值强制转换为float类型
    s1 = data[0:45000*4:4]                              #list切片L[n1:n2:n3]  n1代表开始元素下标；n2代表结束元素下标
                                                        #n3代表切片步长，可以不提供，默认值是1，步长值不能为0
###################################################################################################################

#滤波
###################################################################################################################
    fs = 3000                                           #设立频率变量fs
    lowcut = 1
    highcut = 30
    order = 2                                           #设立滤波器阶次变量
    nyq = 0.5*fs                                        #设立采样频率变量nyq，采样频率=fs/2。
    low = lowcut/nyq
    high = highcut/nyq
    b,a = signal.butter(order,[low,high],btype='band')  #设计巴特沃斯带通滤波器 “band”
    s1_filter1 = signal.lfilter(b,a,s1)                 #将s1带入滤波器，滤波结果保存在s1_filter1中
###################################################################################################################
  
#进行每一秒为一帧的剪断
###################################################################################################################
    l = 0
    data_sec = {}                                       #为保存帧数据的数组进行预定义
    for i in range(300):                                 #设置循环300次
        data_sec[i] = s1_filter1[l:l+150]              #根据采样频率，设置每3000个数据为一组
        l = l + 150  
###################################################################################################################

#为数据添加属性值
###################################################################################################################
    #平均值
    data_mean = np.zeros(300)                            #为保存属性值的数组预先定义一个零矩阵
    for i in range(300):
        data_mean[i] = np.mean(data_sec[i])             #计算数据的平均值

    #方差
    data_var = np.zeros(300)
    for i in range(300):
        data_var[i] = np.var(data_sec[i])               #计算数据的方差

    #离散小波变换
    data_dwt_appro = np.zeros(300)                       #由离散小波变换得到的近似信号，也就是低频信息
    data_dwt_detail = np.zeros(300)                      #由离散小波变换得到的细节信号，也就是高频信号
    for i in range(300):
        Appro, Detail = pywt.dwt(data_sec[i],'db4')     #根据阅读的文献，4阶Daubechies小波拥有最佳的对于EEG信号的处理效果，因此选择db4小波
        data_dwt_appro[i] = np.mean(Appro)              #对小波变换得到的数据计算均值
        data_dwt_detail[i] = np.mean(Detail)
    data_dwt = [data_dwt_appro,data_dwt_detail]
    
    #样本熵
    data_sampen = np.zeros(300)
    for i in range(300):
        data_temp = sampen2(data_sec[i])                #使用sampen模块中的sampen2函数进行样本熵的计算
        data_temp2 = data_temp[2]                       #由于该函数会生成一个二维矩阵，而我们只需要第三个数组中的第二个数据
        data_sampen[i] = data_temp2[1]
    
    #赫斯特指数
    data_ApEn = np.zeros(300)
    for i in range(300):
        data_ApEn[i] = hurst(data_sec[i])               #使用pyeeg模块中的hurst函数计算赫斯特指数

    #Petrosian分形维数
    data_pfd = np.zeros(300)
    for i in range(300):
        data_pfd[i] = pfd(data_sec[i])                  #使用pyeeg模块中的pfd计算Petrosian分形维数
###################################################################################################################

###################################################################################################################
    #打标签
    data_label = np.zeros(300)                          #为对数据打标签做准备
    for i in range(300):                                
        temp_ptp = np.ptp(data_sec[i])                  #利用数据的极值来进行判断包含sharp_wave的情况
        if temp_ptp < 0.05:                             #当极值小于0.05时，表示不包含sharp_wave
            data_label[i] = 0
        elif temp_ptp <0.1:                             #当极值小于0.1，大于等于0.05时，表示包含半个sharp_wave
            data_label[i] = 1
        else:                                           #当极值大于等于0.1时，表示包含一整个sharp_wave
            data_label[i] = 2
###################################################################################################################    

#将所有的属性值保存到xlsx文件中
###################################################################################################################
    data_contribute = np.array([data_label,data_mean,data_var,data_dwt_appro,data_dwt_detail,data_sampen,data_ApEn,data_pfd]).T 
    #print(data_contribute)
    save_in_xlsx(data_contribute,'result_%d'%name)
    name = name + 1
    

