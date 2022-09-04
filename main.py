import hashlib
import json
import requests
import datetime
import time
from urllib.parse import urlencode
import os


info = os.environ.get('INFO', '').split('\n')
answers = os.environ.get('ANS', '').split('\n')
agent = os.environ.get('AGENT', '')

username = info[0]
password = info[1]
latitude = info[2]
longitude = info[3]

# 请求头
headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "User-Agent": agent,
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "2",
    "Host": "student.wozaixiaoyuan.com",
    "Accept-Language": "en-us,en",
    "host": "student.wozaixiaoyuan.com",
    "Accept": "application/json, text/plain, */*"
}


# 定义用密码登录的函数
def login(username, password):
    # 登陆接口
    loginUrl = "https://student.wozaixiaoyuan.com/basicinfo/mobile/login/username"
    url = loginUrl + "?username=" + username + "&password=" + password
    session = requests.session()

    # 请求体（必须有） body = "{}"
    body = "{}"

    response = session.post(url=url, data=body, headers=headers)
    res = json.loads(response.text)

    if res["code"] == 0:
        print("登陆成功")
        # 登录成功获取JWSESSION
        jwsession = response.headers['JWSESSION']
        return jwsession
    else:
        print("登陆失败，请检查账号信息和密码是否正确")
        return False


def getLoction(latitude, longitude):
    url = "https://apis.map.qq.com/ws/geocoder/v1/?key=A3YBZ-NC5RU-MFYVV-BOHND-RO3OT-ABFCR&location={},{}".format(
        longitude, latitude)
    res = requests.get(url)
    resList = res.json()

    if resList["status"] == 0:
        result = resList["result"]
        address_component = result["address_component"]
        address_reference = result["address_reference"]
        ad_info = result["ad_info"]

        city = address_component["city"]
        district = address_component["district"]
        province = address_component["province"]
        township = address_reference["town"]["title"]
        street = address_component["street"]
        areacode = ad_info["adcode"]
        towncode = address_reference["town"]["id"]
        citycode = ad_info["city_code"]

        locationList = [city, district, province, township, street, areacode, towncode, citycode]

        return locationList


class Do:
    def __init__(self):
        self.headers = headers
        # 请求体（必须有） self.body = "{}"
        self.body = "{}"

    def run(self):
        lo = login(username, password)

        if not lo:
            print("登录失败!有可能是账号或密码错误")
        else:
            url = "https://student.wozaixiaoyuan.com/health/save.json"  # 健康打卡 提交地址
            locationList = getLoction(latitude, longitude)

            # 健康打卡数据
            data = {
                "answers": answers,
                "latitude": latitude,  # 维度
                "longitude": longitude,  # 经度
                "country": "中国",
                "city": locationList[0],
                "district": locationList[1],
                "province": locationList[2],
                "township": locationList[3],
                "street": locationList[4],
                "areacode": locationList[5],
                "towncode": locationList[6],
                "citycode": locationList[7]
            }

            time_t = int(round(time.time() * 1000))

            content = f"{locationList[2]}_{time_t}_{locationList[0]}"
            signature = hashlib.sha256(content.encode('utf-8')).hexdigest()

            data["timestampHeader"] = time_t
            data["signatureHeader"] = signature

            self.headers["JWSESSION"] = lo
            print("JWsession--> " + self.headers["JWSESSION"])
            print("当前时间--> ", datetime.datetime.now())
            data = urlencode(data)
            res = requests.post(url=url, headers=self.headers, data=data)  # 健康打卡提交
            res_text = res.json()
            print("res-->", res_text)
            if res_text["code"] == 0:
                print("打卡成功")
            elif res_text["code"] == 1:
                print("message", res_text["message"])
            else:
                print("打卡失败")


if __name__ == "__main__":
    uses = Do()
    uses.run()
