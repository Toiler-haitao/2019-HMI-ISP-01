#coding=utf-8
#!/usr/bin/env python

from aip import AipOcr
import Translate
import numpy as np
from PIL import Image, ImageDraw, ImageFont
#读取本地图片测试
def Get_Image():
    with open('./HTML/0.jpg', 'rb') as fp:
        return fp.read()

#创建客户端
def Create_Client():
    APP_ID = '17517601'
    API_KEY = 'FLjwlLDSGb7tsZfpzgO00F6D'
    SECRET_KEY = '8yGi1u18NMiIrxgckn74wgnPG9uO2cMl'
    return AipOcr(APP_ID, API_KEY, SECRET_KEY)
#识别字体
def Recognize_Word(Image,client):
    Reswords=[]
    TransWords=[]
    client.general(Image)
    options = {}
    options["recognize_granularity"] = "big"
    options["language_type"] = "CHN_ENG"
    options["detect_direction"] = "true"
    options["detect_language"] = "true"
    options["vertexes_location"] = "true"
    options["probability"] = "true"

    Result=client.general(Image, options)
    Res1=Result.items()
    Res2=0
    Left=[]
    top=[]
    width=[]
    height=[]
    Num=0
    matrix=[[0,0],[0,0],[0,0],[0,0]]
    cnt_i=0
    cnt_j=0
    cnt_Num=0
    for i,j in Res1:
        if(isinstance(j,list)):
            for m in j:
                Res2=m.items()
                #print(m)
                for i0,j0 in Res2:
                    if (isinstance(j0, dict)):
                        if str(i0)=='location':
                            Res3=j0.items()
                            #print(Res3)
                            for i1,j1 in Res3:
                                if str(i1)=='left':
                                    Left.append(j1)
                                elif str(i1)=='top':
                                    top.append(j1)
                                elif str(i1) == 'width':
                                    width.append(j1)
                                elif str(i1) == 'height':
                                    height.append(j1)
                                    Num=Num+1
                    elif (isinstance(j0, list)):
                        if str(i0)=='vertexes_location':
                            for s in j0:
                                for m in s.values():
                                    #print(type(m),m,cnt_i,cnt_j)
                                    matrix[cnt_i][cnt_j]=m
                                    cnt_j = cnt_j + 1
                                cnt_i = cnt_i + 1
                                cnt_j=0
                            cnt_i=0
                    else:
                        Reswords.append(j0)
    cnt_Num=Num
    while cnt_Num>0:
        TransWords.append(Translate.Translate_Chinese_To_English(str(Reswords[Num-cnt_Num])))
        cnt_Num=cnt_Num-1

    return Left,top,width,height,Num,Reswords,TransWords
if '__main__' == __name__:
    Img=Get_Image()
    Client=Create_Client()
    Left,top,width,height,Num,Reswords,TransWords=Recognize_Word(Img,Client)
    print(TransWords)