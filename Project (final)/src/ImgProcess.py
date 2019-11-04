#!/usr/bin/env python
# coding: utf-8

# In[1]:


import base64
import urllib
import urllib.request
import cv2
from multiprocessing import Process, Queue
import os

access_token = '24.3a8df80dc63ce8ac24ec1a7b115f2d5f.2592000.1574820093.282335-17330240'
__VideoIndex__ = './Data/WIN_20190927_12_48_37_Pro.mp4'
#__VideoIndex__ = None


# In[2]:


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
    return ref,frame
    
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


#internal trig function
def _TrigGen(body_parts):
    if body_parts:
        #print('left w - left s = ',abs(body_parts['left_wrist']['y'] - body_parts['left_shoulder']['y']))
        #print('right w - right s = ' , abs(body_parts['right_wrist']['y'] - body_parts['right_shoulder']['y']))
        
        if abs(body_parts['left_wrist']['y'] - body_parts['left_shoulder']['y']) < 30 or             abs(body_parts['right_wrist']['y'] - body_parts['right_shoulder']['y']) < 30:
            return 1
        
        return 0
    else:
        raise Exception("content is None")



# trigger the latter function.
trigger_list = []# direct trig res
trigger_res_list = []
trig_frame_wait = 0
def Trigger(body_parts):
    result = 0
    global trigger_list
    global trigger_res_list
    global trig_frame_wait
    
    LIST_INDEX_MAX = 10
    RES_INDEX_MAX = 10
    
    if not trig_frame_wait:

        
        cur_res = 0
        cur_trig = _TrigGen(body_parts)
        trigger_list = trigger_list + [cur_trig]
        sum_list_index = 0
        sum_trig_index = 0
        
        for i in range(2):#0-1
            sum_list_index = sum_list_index + trigger_list.count(i)
        if sum_list_index > LIST_INDEX_MAX: #
            trigger_list = trigger_list[-LIST_INDEX_MAX:]
            sum_list_index = LIST_INDEX_MAX
            
        for i in range(3):#0-1
            sum_trig_index = sum_trig_index + trigger_res_list.count(i)
        if sum_trig_index > RES_INDEX_MAX: #
            trigger_res_list = trigger_res_list[-RES_INDEX_MAX:]
            sum_trig_index = RES_INDEX_MAX
            
        if sum_list_index == LIST_INDEX_MAX:
            if trigger_list.count(1) > 6:
                cur_res = 1
            if trigger_list.count(0) > 6:
                cur_res = 2
            
            trigger_res_list = trigger_res_list + [cur_res]
        
        if sum_list_index == LIST_INDEX_MAX and sum_trig_index == RES_INDEX_MAX:
            if trigger_res_list[:6].count(1) > 5 and trigger_res_list[-4:].count(2) > 3:
                result = 1
                trig_frame_wait = 200
    else:
        trig_frame_wait = trig_frame_wait - 1
    print(trigger_list)
    print(trigger_res_list)
    return result
        
    
        
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
                    #print("\r",body_parts,end="",flush=True)
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
    
    
    
def PutQueue(img_q,img):
    if img_q.qsize()<500:
        img_q.put(img)
    else:
        img_q.get(True)
        img_q.put(img)
        
def OutputMov(img_q,rcd_index):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 保存视频的编码
    

    out = cv2.VideoWriter('outeeput'+str(rcd_index)+'.mp4',fourcc, 20.0, (640,480))
    #while not img_q.empty():
    while img_q.qsize() > 0:
        frame = img_q.get(True)
        out.write(frame)
    out.release()
        
    
'''
多进程
serv_flag_q 是 图像读入后 通知serv开始执行的符号
当serv成功返还res后 serv_p 将flag置空
当检测到servflag 非空时，图像线程将直接进行打印上次结果
'''

def img_p(frame_q,serv_flag_q,res_q,stop_q,img_q1,img_q2):
    
    QUEUE_IN_USE = 1
    RECORD_INDEX = 0
    
    InitVideo()
    
    X_upload = 320
    Y_upload = 240
    X_saveh263 = 640#352
    Y_saveh263 = 480#288
    body_parts =  {'left_wrist': {'y': 1, 'x': 1, 'score': 0}, 'right_wrist': {'y': 1, 'x': 1, 'score': 0}, 'left_shoulder': {'y': 1, 'x': 1, 'score': 0}, 'right_shoulder': {'y': 1, 'x': 1, 'score': 0}}#init body part
    
    for i in range(5000):
        ref,frame_orig = ReadImg()
        if ref == False:
            break
        frame_save = cv2.resize(frame_orig,(X_saveh263,Y_saveh263),interpolation=cv2.INTER_CUBIC)
        #frame_save = frame_orig
        if (QUEUE_IN_USE == 1):
            PutQueue(img_q1,frame_save)
        else:
            PutQueue(img_q2,frame_save)
            
        frame = cv2.resize(frame_orig,(X_upload,Y_upload),interpolation=cv2.INTER_CUBIC)
        frame = ImgPreprocess(frame)
        res = 0 
        if serv_flag_q.qsize() == 0:#如果服务器闲 serv_q is empty
            #print('serv_p is idle')
            if res_q.qsize() > 0:#如果服务器有返回的res,res_q is not empty
                res = res_q.get(True)
            #print('write a frame')
            frame_q.put(frame)
            while frame_q.qsize() == 0:
                True
            #print('start a serv')
            serv_flag_q.put(1)#置服务器忙状态
            
        if res:
            
            res = eval(str(res, encoding = "utf-8"))
            #print(res)
            
            
            if 'person_num' in res:
                if res['person_num'] >0:        
                    for i in body_parts:
                        body_parts[i] = res['person_info'][0]['body_parts'][i]
                    #print("\r",body_parts,end="",flush=True)
            
            trig = Trigger(body_parts)
            print("trigger = ",trig)
            if trig:#
                if QUEUE_IN_USE == 1:
                    OutputMov(img_q1,RECORD_INDEX)
                else:
                    OutputMov(img_q2,RECORD_INDEX)
                RECORD_INDEX = RECORD_INDEX + 1
            
            
            #人脸使用
            #if res['error_code'] == 0:

                #KeyPointRes = KeyPointDetect(frame)
                #print(1)

        
        # print body_parts
        for i in body_parts:
            if body_parts[i]['score']>0.3:
                cv2.circle(frame_orig,(int(body_parts[i]['x']/X_upload*frame_orig.shape[1]),int(body_parts[i]['y']/Y_upload*frame_orig.shape[0])),10,(0,255,255),4)
        #print(body_parts)
        cv2.imshow("1",frame_orig)
        cv2.waitKey(1)
        
    
    
    print('start stopping')
    while img_q1.qsize()>0:
        img_q1.get(True)
    while img_q2.qsize()>0:
        img_q2.get(True)
    print(img_q1.qsize())
    print(img_q2.qsize())
    stop_q.put(1)
    cv2.destroyAllWindows()
    ReleaseVideo()
    
    

def serv_p(frame_q,serv_flag_q,res_q,stop_q):
    while(stop_q.qsize()==0):
        if not serv_flag_q.qsize()>0:#如果置位了服务器忙信号 serv flag is not empty
            #if frame_q.qsize()==0:#如果此时frame队列没有东西，则应该是脑子出了问题
                #raise Exception('Frame is empty')
            
            frame = frame_q.get(True)#提取图像
            print('get a frame')
            res = ImgService(frame)#提交服务器
            if res_q.qsize()>0:
                raise Exception('Res is not empty')
            res_q.put(res)
            #print('stop a serv')
            serv_flag_q.get(True)#取消服务器忙信号
    print('serv_p_stopped')


# In[3]:


f_q = Queue()
s_q = Queue()
r_q = Queue()
st_q = Queue()
img_q1 = Queue()
img_q2 = Queue()
pi = Process(target = img_p, args = (f_q,s_q,r_q,st_q,img_q1,img_q2))
ps = Process(target = serv_p, args = (f_q,s_q,r_q,st_q,))
pi.start()
ps.start()
pi.join()



