#!/usr/bin/env python
# coding: utf-8

# In[1]:


import base64
import urllib
import urllib.request
import cv2
from multiprocessing import Process, Queue
import os

access_token = '24.46a59369c77ecda08838e4cf097e1bf6.2592000.1571900094.282335-17330240'
#__VideoIndex__ = '.\Data\WIN_20190927_12_48_37_Pro.mp4'
__VideoIndex__ = None


# In[25]:


'''
图像预处理
'''
def ImgPreprocess(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    (b,g,r) = cv2.split(frame)
    #b = cv2.equalizeHist(b)
    #g = cv2.equalizeHist(g)
    r = cv2.equalizeHist(r)
    frame = cv2.merge((b,g,r))
    frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
    return frame


'''
人体关键点识别
'''
def KeyPointDetect(img_base64):
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis"
    params = {"image":img_base64}

    params = urllib.parse.urlencode(params)
    request_url = request_url + "?access_token=" + access_token

    params = params.encode('utf-8')
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    request = urllib.request.Request(url=request_url, data=params, headers = header)

    response = urllib.request.urlopen(request)
    content = response.read()

    if content:
        return content
    else:
        return None

'''
人脸检测与属性分析
'''
def FaceDetect(img_base64):
    # encoding:utf-8

    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
    
    params = {"image":img_base64,"image_type":"BASE64","face_field":"faceshape,facetype"}
    params = urllib.parse.urlencode(params)
    
    params = params.encode('utf-8')
    request_url = request_url + "?access_token=" + access_token
    header = {'Content-Type': 'application/json'}
    request = urllib.request.Request(url=request_url, data=params, headers = header)

    response = urllib.request.urlopen(request)
    content = response.read()
    if content:
        #content = eval(str(content, encoding = "utf-8"))
        return content
    else:
        return None

    
def ExtractFacePoint(res, frame, face_index = 0, graph = False):
    
    face_location = res['result']['face_list'][face_index]['location']
    face_lefttop = (int(face_location['left']),int(face_location['top']))
    face_rightdown = (int(face_location['left'] + face_location['width']), int(face_location['top'] + face_location['height']))
    
    if graph == True:
        cv2.rectangle(frame,face_lefttop, face_rightdown,(255,255,255),1,4)
    
    return (face_lefttop, face_rightdown, frame)
    
    
'''
配置视频输入流
'''
def InitVideo():
    global capture

    if __VideoIndex__:
        capture = cv2.VideoCapture(__VideoIndex__)
    else:
        capture = cv2.VideoCapture(0)

    if capture.isOpened():
        return True
    else:
        raise Exception("camera failed")

'''
释放视频输入设备
'''
def ReleaseVideo():
    capture.release()

'''
调用摄像头返回图像
'''
def ReadImg():
    ref,frame = capture.read()
    if ref == True:
        return frame
    else:
        return None
    
def SaveImg(frame):
    cv2.imwrite('temp_0.jpg',frame)
    
'''
np图像转base64编码
'''
def Img2Base64(img):
    img_temp = cv2.imencode('.jpg',img)[1]
    img_base64 = base64.b64encode(img_temp)
    img_base64 = str(img_base64, encoding='utf-8')
    return img_base64

def LoadImgFile():
    with open('temp_0.jpg','rb') as f:
        img = base64.b64encode(f.read())
    return img

def Trigger(KeyPointContent):
    if KeyPointContent:
        print(KeyPointContent)
    else:
        raise Exception("content is None")
        
'''
服务器申请函数
'''
def ImgService(frame):
    SaveImg(frame)
    img_base64 = LoadImgFile()
    res = KeyPointDetect(img_base64)
    return res
        
'''
图像处理主函数，测试用
'''
def ImgProcess():
    InitVideo()
    for i in range(50):
        frame = ReadImg()
        frame = cv2.resize(frame,(640,480),interpolation=cv2.INTER_CUBIC)
        frame = ImgPreprocess(frame)
        res = ImgService(frame)
        #res = None
        if res:
            res = eval(str(res, encoding = "utf-8"))
            #print(res)

            body_parts = {'left_wrist':0,'right_wrist':0, 'left_shoulder':0, 'right_shoulder':0}
            if 'person_num' in res:
                if res['person_num'] == 1:        
                    for i in body_parts:
                        body_parts[i] = res['person_info'][0]['body_parts'][i]
                    print("\r",body_parts,end="",flush=True)
                    for i in body_parts:
                        if body_parts[i]['score']>0.5:
                            cv2.circle(frame,(int(body_parts[i]['x']),int(body_parts[i]['y'])),10,(0,255,255),4)
            
            #人脸使用
            #if res['error_code'] == 0:

                #KeyPointRes = KeyPointDetect(frame)
                #print(1)

        cv2.imshow("1",frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()
    ReleaseVideo()
    
    
'''
多进程
serv_flag_q 是 图像读入后 通知serv开始执行的符号
当serv成功返还res后 serv_p 将flag置空
当检测到servflag 非空时，图像线程将直接进行打印上次结果
'''

def img_p(frame_q,serv_flag_q,res_q,stop_q):
    InitVideo()
    body_parts =  {'left_wrist': {'y': 1, 'x': 1, 'score': 0}, 'right_wrist': {'y': 1, 'x': 1, 'score': 0}, 'left_shoulder': {'y': 1, 'x': 1, 'score': 0}, 'right_shoulder': {'y': 1, 'x': 1, 'score': 0}}#init body part
    for i in range(500):
        frame = ReadImg()
        frame = cv2.resize(frame,(320,240),interpolation=cv2.INTER_CUBIC)
        frame = ImgPreprocess(frame)
        res = 0 
        if serv_flag_q.empty():#如果服务器闲 serv_q is empty
            print('serv_p is idle')
            if not res_q.empty():#如果服务器有返回的res,res_q is not empty
                res = res_q.get(True)
            print('write a frame')
            frame_q.put(frame)
            print('start a serv')
            serv_flag_q.put(1)#置服务器忙状态
            
        if res:
            
            res = eval(str(res, encoding = "utf-8"))
            #print(res)
            
            
            if 'person_num' in res:
                if res['person_num'] == 1:        
                    for i in body_parts:
                        body_parts[i] = res['person_info'][0]['body_parts'][i]
                    #print("\r",body_parts,end="",flush=True)
                    

            
            #人脸使用
            #if res['error_code'] == 0:

                #KeyPointRes = KeyPointDetect(frame)
                #print(1)

        
        
        for i in body_parts:
            if body_parts[i]['score']>0.3:
                cv2.circle(frame,(int(body_parts[i]['x']),int(body_parts[i]['y'])),10,(0,255,255),4)
        print(body_parts)
        cv2.imshow("1",frame)
        cv2.waitKey(1)
        
    stop_q.put(1)
    cv2.destroyAllWindows()
    ReleaseVideo()
    
    

def serv_p(frame_q,serv_flag_q,res_q,stop_q):
    while(stop_q.empty()):
        if not serv_flag_q.empty():#如果置位了服务器忙信号 serv flag is not empty
            if frame_q.empty():#如果此时frame队列没有东西，则应该是脑子出了问题
                raise Exception('Frame is empty')
            print('get a frame')
            frame = frame_q.get(True)#提取图像
            res = ImgService(frame)#提交服务器
            if not res_q.empty():
                raise Exception('Res is not empty')
            res_q.put(res)
            print('stop a serv')
            serv_flag_q.get(True)#取消服务器忙信号





if __name__ == '__main__':
    f_q = Queue()
    s_q = Queue()
    r_q = Queue()
    st_q = Queue()
    pi = Process(target = img_p, args = (f_q,s_q,r_q,st_q,))
    ps = Process(target = serv_p, args = (f_q,s_q,r_q,st_q,))
    pi.start()
    ps.start()
    pi.join()




