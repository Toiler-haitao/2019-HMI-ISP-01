# coding=utf-8

import sys
import json
import base64
import time
import pyaudio
import wave

IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    timer = time.perf_counter
else:
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode
    if sys.platform == "win32":
        timer = time.clock
    else:
        # On most other platforms the best timer is time.time()
        timer = time.time

API_KEY = 'kVcnfD9iW2XVZSMaLMrtLYIz'
SECRET_KEY = 'O9o1O213UgG5LFn0bDGNtoRN3VWl2du6'

# 普通版
DEV_PID = 1536
ASR_URL = 'http://vop.baidu.com/server_api'
# 极速版
#DEV_PID = 80001
#ASR_URL = 'https://vop.baidu.com/pro_api'

token = '24.9d7d643527ee67f41ed64f11e5b58444.2592000.1573186085.282335-15803531'

CHUNK = 1024
RATE = 16000
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("开始录音,请说话......")

frames = []

for i in range(0, int(RECORD_SECONDS * RATE / CHUNK)):
    data = stream.read(CHUNK)
    frames.append(data)

print("录音结束,请闭嘴!")

stream.stop_stream()
stream.close()
p.terminate()

speech_data = b''.join(frames)
speech = base64.b64encode(speech_data)
speech_str = str(speech, 'utf-8')
length = len(speech_data)

params = {'dev_pid': DEV_PID,
         #"lm_id" : LM_ID,    #测试自训练平台开启此项
          'format': 'pcm',
          'rate': RATE,
          'token': token,
          'cuid': 'hmi-test',
          'channel': 1,
          'speech': speech_str,
          'len': length
          }

post_data = json.dumps(params, sort_keys=False)
req = Request(ASR_URL, post_data.encode('utf-8'))
req.add_header('Content-Type', 'application/json')

try:
    begin = timer()
    f = urlopen(req)
    result_str = f.read()
    print ("Request time cost %f" % (timer() - begin))
except URLError as err:
    print('asr http response http code : ' + str(err.code))
    result_str = err.read()
result_str = str(result_str, 'utf-8')

result = json.loads(result_str)
print(result)
if result['err_no'] == 0:
    print(result['result'])
