# -*- coding: utf-8 -*-
"""
Date : 2021/5/3 7:24
Author : 小康
description ：每日清晨问候-Github Action驱动
Site : www.xiaokang.cool
微信公众号: 小康新鲜事儿
微信小程序： 小康的宝藏库
"""
import requests
import simplejson as json
from lxml import etree
import fake_useragent
import uuid
import datetime
import time
from hashlib import md5
import logging
from optparse import OptionParser

filelog = logging.FileHandler(filename='./morning_greetings_action.log', mode='a', encoding='utf-8')
fmt = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s :  %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
filelog.setFormatter(fmt)
logger1 = logging.Logger(name='morning_greetings_action', level=logging.DEBUG)
logger1.addHandler(filelog)

gettoken_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}"
url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}"
headers = {'Content-Type': "application/x-www-form-urlencoded"}
uids = 'xiaokang'
agentId = 1000002
part_dict = {"人力": 2, "开发": 3, "行政": 4, "销售": 5, "财务": 6, "不群发部门": "@all"}
usage = "python MorningGreetings.py --user kangchengjie --party 1" \
        " --corpid xxx --corpsecret xxx"


def get_fake_ua():
    ua = fake_useragent.UserAgent()
    headers = {
        'user-agent': ua.random
    }
    return headers


# 解析参数
def parse_args():
    args = {}
    parser = OptionParser(usage=usage)
    parser.add_option("--user", action="store", dest="user", help="--user kangchengjie")
    parser.add_option("--party", action="store", dest="party", help="--party 1")
    parser.add_option("--corpid", action="store", dest="corpid", help="--corpid xxx")
    parser.add_option("--corpsecret", action="store", dest="corpsecret", help="--corpsecret xxx")
    (options, _) = parser.parse_args()
    # 判断参数是否为空
    if options.user is None:
        parser.print_help()
        sys.exit()
    else:
        args["user"] = options.user

    if options.party is None:
        parser.print_help()
        sys.exit()
    else:
        args["party"] = options.party

    if options.corpid is None:
        parser.print_help()
        sys.exit()
    else:
        args["corpid"] = options.corpid

    if options.corpsecret is None:
        parser.print_help()
        sys.exit()
    else:
        args["corpsecret"] = options.corpsecret
    return args


# 获取access_token
def get_access_token(corpid, corpsecret):
    try:
        res = requests.request("GET", gettoken_url.format(corpid, corpsecret))
        access_token = json.loads(res.content).get("access_token")
    except Exception as e:
        logger1.error("获取access_token失败,错误详情：{}".format(e))
    if access_token != None:
        return access_token
    return None


# 主逻辑，发送消息至企业微信号
def send_wechat(contents, users, party, corpid, corpsecret):
    """
    发送至企业微信号
    :param contents: 渲染模板出来的内容
    :param users: 成员ID列表
    :param party: 部门ID
    :return:
    """
    msg_id = uids + str(uuid.uuid4()).replace("-", "")[-11:]
    nonces = str(uuid.uuid4()).replace("-", "")[-24:]
    timestamps = int(time.time() * 1000)
    access_token = get_access_token(corpid, corpsecret)
    logger1.info("access_token值：{}".format(access_token))
    s = md5(
        str("nonce={}".format(nonces) + "&" + "timestamp={}".format(
            timestamps) + "&" + "uid={}".format(uids)).encode("utf-8"))
    signature = s.hexdigest()
    logger1.info("数据签名：{}".format(signature))
    msg_data = {
        "touser": "{}".format(users),
        "toparty": "{}".format(party),
        "totag": "@all",
        "msgtype": "text",
        "agentid": "{}".format(agentId),
        "text": {
            "content": "{}".format(contents)
        },
        "safe": 0,
        "msg_id": "{}".format(msg_id),
        "signature": "{}".format(signature)
    }
    # 请求体
    payload = json.dumps(msg_data)
    logger1.info("发送信息：{}".format(payload))
    try:
        response = requests.request("POST", url.format(access_token), data=payload, headers=headers)
    except Exception as e:
        logger1.error("发送企业消息失败,详情:{}".format(response.text))
    logger1.info("return info : {}".format(response.text))


def get_week_day(date):
    week_day_dict = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期天',
    }
    day = date.weekday()
    return "今天日期为：" + str(datetime.date.today()) + ' ' + week_day_dict[day]


def get_weather():
    url = "https://d1.weather.com.cn/sk_2d/101010100.html?_=1618886817920"
    r_url = requests.get(url, headers=get_fake_ua(), verify=False)
    message = json.loads(r_url.text.encode("latin1").decode("utf8").replace("var dataSK = ", ""))
    cityname = message['cityname']
    aqi = int(message['aqi'])
    sd = message['sd']
    wd = message['WD']
    ws = message['WS']
    temp = message['temp']
    weather = message['weather']
    if aqi <= 50:
        airQuality = "优"
    elif aqi <= 100:
        airQuality = "良"
    elif aqi <= 150:
        airQuality = "轻度污染"
    elif aqi <= 200:
        airQuality = "中度污染"
    elif aqi <= 300:
        airQuality = "重度污染"
    else:
        airQuality = "严重污染"
    return cityname + " " + '今日天气：' + weather + ' 温度：' + temp + ' 摄氏度 ' + wd + ws + ' 相对湿度：' + sd + ' 空气质量：' \
           + str(aqi) + "（" + airQuality + "）"


def get_top_list():
    url = "http://top.baidu.com/"
    r = requests.get(url, headers=get_fake_ua())
    r.encoding = 'gb2312'
    tree = etree.HTML(r.text)
    li_list = tree.xpath('//*[@id="hot-list"]/li')
    top_list = []
    for li in li_list:
        num = li_list.index(li) + 1
        title = li.xpath('./a/@title')[0]
        top_list.append(str(num) + ':' + title)
    return top_list


def get_daily_sentence():
    url = "http://open.iciba.com/dsapi/"
    r = requests.get(url, headers=get_fake_ua())
    r = json.loads(r.text)
    content = r["content"]
    note = r["note"]
    daily_sentence = content + "\n" + note
    return daily_sentence


def greetings():
    hour = int(time.strftime('%H', time.localtime(time.time())))
    if hour <= 6:
        return "小康，早上好！\n"
    if hour >= 12:
        return "小康，中午好！\n"
    if hour >= 21:
        return "小康，晚上好！\n"
    else:
        return "认真生活,努力长大-Github Action强力驱动"


def get_sendContent():
    sendContent = greetings() + "\n" + get_week_day(datetime.date.today()) + "\n\n" + get_weather() + "\n\n" + str(
        get_top_list()).replace(
        "', '", '\n').replace("['", "").replace("']", "") + "\n\n" + get_daily_sentence()
    return sendContent


def main():
    args = parse_args()
    logger1.info(u"开始发送消息")
    user = args["user"]
    party = args["party"]
    corpid = args["corpid"]
    corpsecret = args["corpsecret"]
    contents = get_sendContent()

    print(contents)
    party_id = part_dict.get(party)
    # 判断用户是否为空
    if (user) != None:
        users = '|'.join(user.split(','))
    else:
        users = ''

    # 判断一下部门是否为空
    if party != None:
        party = party_id
    else:
        party = '@all'
    send_wechat(contents, users, party, corpid, corpsecret)
    logger1.info(u"发送消息结束")


if __name__ == "__main__":
    main()
