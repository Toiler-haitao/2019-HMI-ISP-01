# encoding:utf-8
import base64
import urllib
import urllib.request
import cv2

access_token = '24.46a59369c77ecda08838e4cf097e1bf6.2592000.1571900094.282335-17330240'
#__VideoIndex__ = '.\Data\WIN_20190927_12_48_37_Pro.mp4'
__VideoIndex__ = None


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


if __name__ == "__main__":
    pass
    InitVideo()

    for i in range(100):
        frame = ReadImg()
        frame = cv2.resize(frame,(640,480),interpolation=cv2.INTER_CUBIC)
        SaveImg(frame)
        img_base64 = LoadImgFile()
        res = FaceDetect(img_base64)
        #res = None
        if res:
            res = eval(str(res, encoding = "utf-8"))
            print(res)
            if res['error_code'] == 0:

                face_location = res['result']['face_list'][0]['location']
                face_lefttop = (int(face_location['left']),int(face_location['top']))
                face_rightdown = (int(face_location['left'] + face_location['width']), int(face_location['top'] + face_location['height']))
                cv2.rectangle(frame,face_lefttop, face_rightdown,(255,255,255),1,4)

        cv2.imshow("1",frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()
    ReleaseVideo()
