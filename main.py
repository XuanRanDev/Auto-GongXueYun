import datetime
import json
import os
import random
import sys
import time
from hashlib import md5

import pytz
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

import MessagePush
import Constant

pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep

# 设置重连次数
requests.adapters.DEFAULT_RETRIES = 5

headers = {}


def getPlanId(user, token: str, sign: str):
    url = "https://api.moguding.net:9000/practice/plan/v3/getPlanByStu"
    data = {
        "state": ""
    }
    headers["sign"] = sign
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()["data"][0]["planId"]


def getUserAgent(user):
    if user["user-agent"] != 'null':
        return user["user-agent"]
    return random.choice([
        'Mozilla/5.0 (Linux; U; Android 9; zh-cn; Redmi Note 5 Build/PKQ1.180904.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.10.8',
        'Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.2.3 (Baidu; P1 9)',
        'Mozilla/5.0 (Linux; Android 10; EVR-AL00 Build/HUAWEIEVR-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Mobile Safari/537.36 baiduboxapp/11.0.5.12 (Baidu; P1 10)',
        'Mozilla/5.0 (Linux; Android 9; JKM-AL00b Build/HUAWEIJKM-AL00b; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045130 Mobile Safari/537.36 MMWEBID/8951 MicroMessenger/7.0.12.1620(0x27000C36) Process/tools NetType/4G Language/zh_CN ABI/arm64',
        'Mozilla/5.0 (Linux; Android 8.1.0; PBAM00 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.0.14 (Baidu; P1 8.1.0) NABar/2.0',
        'Mozilla/5.0 (Linux; Android 10; LIO-AN00 Build/HUAWEILIO-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 XWEB/1170 MMWEBSDK/200201 Mobile Safari/537.36 MMWEBID/3371 MicroMessenger/7.0.12.1620(0x27000C36) Process/toolsmp NetType/4G Language/zh_CN ABI/arm64'
    ])


def getSign2(text: str):
    s = text + "3478cbbc33f84bd00d75d7dfa69e0daa"
    return md5(s.encode("utf-8")).hexdigest()


def parseUserInfo():
    allUser = ''
    if os.path.exists(pwd + "user.json"):
        print(Constant.findUserJsonFile)
        with open(pwd + "user.json", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                allUser = allUser + line + '\n'
    else:
        return json.loads(os.environ.get("USERS", ""))
    return json.loads(allUser)


def save(user, userId: str, token: str, planId: str, country: str, province: str,
         address: str, signType: str = "START", description: str = "",
         device: str = "Android", latitude: str = None, longitude: str = None):
    text = device + signType + planId + userId + f"{country}{province}{address}"
    headers["sign"] = getSign2(text=text)
    data = {
        "country": country,
        "address": f"{country}{province}{address}",
        "province": province,
        "city": province,
        "latitude": latitude,
        "description": description,
        "planId": planId,
        "type": signType,
        "device": device,
        "longitude": longitude
    }
    url = "https://api.moguding.net:9000/attendence/clock/v2/save"
    res = requests.post(url=url, headers=headers, data=json.dumps(data))
    return res.json()["code"] == 200, res.json()["msg"]


def encrypt(key, text):
    aes = AES.new(key.encode("utf-8"), AES.MODE_ECB)
    pad_pkcs7 = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
    res = aes.encrypt(pad_pkcs7)
    msg = res.hex()
    return msg


def getToken(user):
    url = "https://api.moguding.net:9000/session/user/v3/login"
    t = str(int(time.time() * 1000))
    data = {
        "password": encrypt("23DbtQHR2UMbH6mJ", user["password"]),
        "phone": encrypt("23DbtQHR2UMbH6mJ", user["phone"]),
        "t": encrypt("23DbtQHR2UMbH6mJ", t),
        "loginType": user["type"],
        "uuid": ""
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers)
    return res.json()


def useUserTokenSign(user):
    headers["authorization"] = user["token"]
    phone = user["phone"]
    token = user["token"]
    userId = user["userId"]
    planId = user["planId"]
    signStatus = startSign(userId, token, planId, user, startType=0)
    if signStatus:
        print(Constant.tokenSignWarning)
        print(Constant.tokenSignRetry)
        MessagePush.pushMessage(phone, Constant.tokenSignError, Constant.tokenSignErrorDesc, user["pushKey"])
        prepareSign(user, keepLogin=False)


def prepareSign(user, keepLogin=True):
    if not user["enable"]:
        return

    if user["keepLogin"] and keepLogin:
        # 启用了保持登录状态，则使用设备Token登录
        useUserTokenSign(user)
        return

    userInfo = getToken(user)
    phone = user["phone"]

    if userInfo["code"] != 200:
        print(Constant.signError + userInfo["msg"])
        MessagePush.pushMessage(phone, Constant.signErrorNotifyTitle,
                                '用户：' + phone + ',' + Constant.signError + userInfo["msg"],
                                user["pushKey"])
        return

    userId = userInfo["data"]["userId"]
    token = userInfo["data"]["token"]

    sign = getSign2(userId + 'student')
    planId = getPlanId(user, token, sign)
    startSign(userId, token, planId, user, startType=1)


# startType = 0 使用保持登录状态签到
# startType = 1 使用登录签到
def startSign(userId, token, planId, user, startType):
    hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
    if hourNow < 12:
        signType = 'START'
    else:
        signType = 'END'
    phone = user["phone"]
    print(Constant.prepareSign)

    latitude = user["latitude"]
    longitude = user["longitude"]
    if user["randomLocation"]:
        latitude = latitude[0:len(latitude) - 1] + str(random.randint(0, 10))
        longitude = longitude[0:len(longitude) - 1] + str(random.randint(0, 10))

    signResp, msg = save(user, userId, token, planId,
                         user["country"], user["province"], user["address"],
                         signType=signType, description='', device=user['type'],
                         latitude=latitude, longitude=longitude)
    if signResp:
        print(Constant.signOK)
    else:
        print(Constant.signNo)
        if not startType:
            print()
            return True

    ######################################
    # 处理推送信息
    pushSignType = '上班'
    if signType == 'END':
        pushSignType = '下班'

    pushSignIsOK = '成功！'
    if not signResp:
        pushSignIsOK = '失败！'

    signStatus = '打卡'

    hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
    if hourNow == 11 or hourNow == 23:
        signStatus = '补签'

    # 推送消息内容构建

    MessagePush.pushMessage(phone, '工学云' + pushSignType + signStatus + pushSignIsOK,
                            '用户：' + phone + '，工学云' + pushSignType + signStatus + pushSignIsOK
                            , user["pushKey"])

    # 消息推送处理完毕
    #####################################

    print(Constant.signFinish)


def signCheck(users):
    for user in users:
        if not user["signCheck"] and user["enable"]:
            continue

        print()
        url = "https://api.moguding.net:9000/attendence/clock/v1/listSynchro"
        if user["keepLogin"]:
            headers["authorization"] = user["token"]
        else:
            headers["authorization"] = getToken(user)["data"]["token"]
        t = str(int(time.time() * 1000))
        data = {
            "t": encrypt("23DbtQHR2UMbH6mJ", t)
        }
        res = requests.post(url=url, headers=headers, data=json.dumps(data))

        if res.json()["msg"] != 'success':
            print(Constant.signCheckError2)
            continue

        lastSignInfo = res.json()["data"][0]
        lastSignDate = lastSignInfo["dateYmd"]
        lastSignType = lastSignInfo["type"]
        hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
        nowDate = str(datetime.datetime.now(pytz.timezone('PRC')))[0:10]
        if hourNow <= 12 and lastSignType == 'END' and lastSignDate != nowDate:
            print(Constant.signCheckRetroactiveStart)
            prepareSign(user)
        if hourNow >= 23 and lastSignType == 'START' and lastSignDate == nowDate:
            print(Constant.signCheckRetroactiveEnd)
            prepareSign(user)
        print(Constant.signCheckTips3)
        continue


def resetHeaders(user):
    global headers
    headers = {
        "roleKey": "student",
        "authorization": "",
        "sign": "",
        "content-type": "application/json; charset=UTF-8",
        "host": "api.moguding.net:9000",
        "user-agent": getUserAgent(user)
    }


if __name__ == '__main__':
    try:
        users = parseUserInfo()
    except Exception as e:
        print(Constant.parseConfigError)
        sys.exit(0)

    hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
    if hourNow == 11 or hourNow == 23:
        print(Constant.signCheckStartTips)
        print(Constant.signCheckStartDesc)
        try:
            signCheck(users)
        except Exception as e:
            print(Constant.parseConfigError + str(e))
        print(Constant.signCheckEndTips)
        sys.exit()

    for user in users:
        resetHeaders(user)
        #TODO 取消注释
        # try:
        #     prepareSign(user)
        # except Exception as e:
        #     print('工学云打卡失败，错误原因：' + str(e))
        #     MessagePush.pushMessage(user["phone"], '工学云打卡失败',
        #                             '工学云打卡失败, 可能是连接工学云服务器超时,但请别担心，' +
        #                             '中午11点以及晚上23点，我们会进行打卡检查，' +
        #                             '如未打卡则会自动补签（在打卡检查启用的情况下）。\n\n\n' +
        #                             '具体错误信息：' + str(e)
        #                             , user["pushKey"])
