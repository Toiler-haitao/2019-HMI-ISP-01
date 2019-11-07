# coding=utf-8

import http.client
import hashlib
import urllib
import random
import json

#中文翻译成英文
def Translate_Chinese_To_English(ChineseStr):
    result='None'
    Resword=[]
    appid = '20191102000351589'
    secretKey = 'iZFt1INdTtjOUpMVC1V2'

    httpClient = None
    myurl = '/api/trans/vip/translate'

    salt = random.randint(32768, 65536)
    q=ChineseStr
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + 'zh' + '&to=' + 'en' + '&salt=' + str(
    salt) + '&sign=' + sign

    Num=0

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

    except Exception as e:
        print (e)
        result='Translate Error!'
    finally:
        if httpClient:
            httpClient.close()

    if isinstance(result,dict):
        for i,j in result.items():
            if isinstance(j,list):
                for m in j:
                    Res=m.items()
                    for i0,j0 in Res:
                        if str(i0)=='dst':
                            Resword.append(j0)
                            Num=Num+1
    if Num>0:
        return Resword[0]
    else:
        return Resword

if '__main__' == __name__:
    print(Translate_Chinese_To_English(str('春天在哪里')))