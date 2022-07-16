# -*- coding: utf-8 -*-
"""
Date : 2021/5/3 7:24
update : 2022/07/16 17:45
Author : 小康
description ：每日清晨问候-Github Action驱动
Site : www.xiaokang.cool
微信公众号: 小康新鲜事儿
微信小程序： 小康的宝藏库
"""
import requests
import simplejson as json
import json
from bs4 import BeautifulSoup
import fake_useragent
import uuid
import datetime
import time
from hashlib import md5
import logging
from optparse import OptionParser
import sys

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


def get_bd_top_list():
    requests_page = requests.get('http://top.baidu.com/buzz?b=1&c=513&fr=topbuzz_b42_c513')
    soup = BeautifulSoup(requests_page.text, "lxml")
    soup_text = soup.find_all("a", class_='list-title')
    i = 0
    top_list = []
    for text in soup_text:
        i += 1
        top_list.append(str(i) + "、" + text.string.encode("latin1").decode("GBK"))
        if i == 10:
            break
    return top_list


def get_wb_top_list():
    url = "https://api.iyk0.com/wbr"
    r = requests.get(url, verify=False)
    r = str("[" + str(r.content).replace("\r\n", ",") + "]").replace(",]", "]")
    wb_list = json.loads(r)
    top_list = []
    for per_wb in wb_list:
        title = per_wb.get('title')
        link = per_wb.get('url')
        top_list.append(str(title) + '\n' + link)
    return top_list


def get_zhihu_list():
    requests.packages.urllib3.disable_warnings()
    url = "https://https-github-com-xiaokangxxs-xiaokang-api.vercel.app/api/news"
    r = requests.get(url, verify=False)
    resp = json.loads(r.text)
    weiyu = resp.get('data').get('weiyu')
    news = resp.get('data').get('news')
    i = 0
    zhihu_list = []
    for new in news:
        i += 1
        zhihu_list.append(str(i) + "、" + new)
        if i == 10:
            break
    return zhihu_list, weiyu

def get_daily_sentence():
    url = "http://open.iciba.com/dsapi/"
    r = requests.get(url, headers=get_fake_ua())
    r = json.loads(r.text)
    content = r["content"]
    note = r["note"]
    daily_sentence = content + "\n" + note
    return daily_sentence

def get_weather_today():
    try:
        api = 'http://t.weather.itboy.net/api/weather/city/'    #API地址，必须配合城市代码使用
        city_code = '101011000' #进入https://where.heweather.com/index.html查询你的城市代码
        tqurl = api + city_code
        response = requests.get(tqurl)
        d = response.json()         #将数据以json形式返回，这个d就是返回的json数据
        if(d['status'] == 200):     #当返回状态码为200，输出天气状况
            parent = d["cityInfo"]["parent"] #省
            city = d["cityInfo"]["city"] #市
            update_time = d["time"] #更新时间
            date = d["data"]["forecast"][0]["ymd"] #日期
            week = d["data"]["forecast"][0]["week"] #星期
            weather_type = d["data"]["forecast"][0]["type"] # 天气
            wendu_high = d["data"]["forecast"][0]["high"] #最高温度
            wendu_low = d["data"]["forecast"][0]["low"] #最低温度
            shidu = d["data"]["shidu"] #湿度
            pm25 = str(d["data"]["pm25"]) #PM2.5
            pm10 = str(d["data"]["pm10"]) #PM10
            quality = d["data"]["quality"] #天气质量
            fx = d["data"]["forecast"][0]["fx"] #风向
            fl = d["data"]["forecast"][0]["fl"] #风力
            ganmao = d["data"]["ganmao"] #感冒指数
            tips = d["data"]["forecast"][0]["notice"] #温馨提示
            # 天气提示内容
            word = "-----------------------------------------" + "\n【今日份天气】\n城市： " + parent + city + \
                   "\n日期： " + date + " 星期: " + week + "\n天气: " + weather_type + "\n温度: " + wendu_high + " / "+ wendu_low + "\n湿度: " + \
                    shidu + "\nPM25: " + pm25 + "\nPM10: " + pm10 + "\n空气质量: " + quality + \
                   "\n风力风向: " + fx + fl + "\n感冒指数: "  + ganmao + "\n温馨提示： " + tips + "\n更新时间: " + update_time
            return word
    except:
        msg='【出现错误】\n　　今日天气推送错误，请检查服务或网络状态！'
        return msg

def greetings():
    hour = int(time.strftime('%H', time.localtime(time.time())))
    if hour <= 8:
        return "小康，早上好！\n"
    if hour >= 12 and hour <= 14:
        return "小康，中午好！\n"
    if hour >= 21 and hour <= 23:
        return "小康，晚上好！\n"
    else:
        return "认真生活,努力长大-Github Action强力驱动"


# def get_sendContent():
#    sendContent = greetings() + "\n" + get_week_day(datetime.date.today()) + "\n\n" + str(
#        get_bd_top_list()).replace(
#        "', '", '\n').replace("['", "").replace("']", "") + "\n\n" + get_daily_sentence() + "\n"
#    return sendContent

def get_sendContent():
	zhihu_list, weiyu = get_zhihu_list()
    sendContent = greetings() + "\n" + get_weather_today() + "\n\n" + str(zhihu_list).replace("', '", '\n').replace("['", "").replace("']", "") + "\n\n" + weiyu + +"\n\n" + get_daily_sentence() + "\n\n"
    return sendContent


def main():
    args = parse_args()
    logger1.info(u"开始发送消息")
    user = args["user"]
    party = args["party"]
    corpid = args["corpid"]
    corpsecret = args["corpsecret"]
    contents = get_sendContent()
    suffix = """![60秒读懂世界](http://api.03c3.cn/zb/)"""
    contents = contents + "\n-----------------------------------------\n" + suffix
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
