#_*_encoding:utf-8_*_
import time
import hashlib
import requests
import json
import argparse

def estimate_communication(audioPath, text):
    #_*_encoding:utf-8_*_
    if text == "":
        return 0
    appKey = "1686115958000171"
    secretKey = "3c477bbcac521e9fa22f6386fd596221"

    baseURL = "https://api.speechsuper.com/"

    timestamp = str(int(time.time()))

    coreType = "para.eval" # Change the coreType according to your needs.
    refText = text # Change the reference text according to your needs.
    print('audio analysis started')
    print(refText)
    audioType = 'wav' # Change the audio type corresponding to the audio file.
    audioSampleRate = 16000
    userId = "guest"

    url =  baseURL + coreType
    connectStr = (appKey + timestamp + secretKey).encode("utf-8")
    connectSig = hashlib.sha1(connectStr).hexdigest()
    startStr = (appKey + timestamp + userId + secretKey).encode("utf-8")
    startSig = hashlib.sha1(startStr).hexdigest()

    params={
        "connect":{
            "cmd":"connect",
            "param":{
                "sdk":{
                    "version":16777472,
                    "source":9,
                    "protocol":2
                },
                "app":{
                    "applicationId":appKey,
                    "sig":connectSig,
                    "timestamp":timestamp
                }
            }
        },
        "start":{
            "cmd":"start",
            "param":{
                "app":{
                    "userId":userId,
                    "applicationId":appKey,
                    "timestamp":timestamp,
                    "sig":startSig
                },
                "audio":{
                    "audioType":audioType,
                    "channel":1,
                    "sampleBytes":2,
                    "sampleRate":audioSampleRate
                },
                "request":{
                    "coreType":coreType,
                    "refText":refText,
                    "tokenId":"tokenId"
                }

            }
        }
    }

    datas=json.dumps(params)
    data={'text':datas}
    headers={"Request-Index":"0"}
    files={"audio":open(audioPath,'rb')}
    res=requests.post(url, data=data, headers=headers, files=files)
    print(res)
    res_data = {'integrity': res.json()['result']['integrity'], 'speed': res.json()['result']['speed'], 'duration':res.json()['result']['duration'], 'rhythm':res.json()['result']['rhythm'], 'fluency':res.json()['result']['fluency'], 'pronumciation': res.json()['result']['pronunciation'], 'overall': res.json()['result']['overall']}

    # print(res.text.encode('utf-8', 'ignore').decode('utf-8'))
    return json.dumps(res_data)
