# -*- coding: utf-8 -*-
"""
线上写一个脚本，拿到eventv4的第一条数据的时间 as online_start_time
拿到当前最后一条的数据的servertime as online_end_time
以start_time和end_time为range做一次count as count
生成json文件 {"start_time":ISODate() , "end_time":ISODate（）,count: INT_number} --> onlineCount.json
/Backup/v4_events_httplogs_orderstuff/monitor/onlineDbCount.json  o2oMongoCounter.py
线下scp onlineCount.json
一个脚本取到start_time,end_time,排除后端埋点情况下做local_count，
local_count - count 看值
如果值特别大，发邮件报警
"""

import pymongo
import sys
from pymongo import MongoClient
from datetime import datetime
import datetime
import json
from StringIO import StringIO
import time
from datetime import date
import calendar
import subprocess
import dateutil.parser
import smtplib
from email.mime.text import MIMEText


db_host = MongoClient("10.8.8.111", 27017)
db_events_v4 = db_host["eventsV4"]
collections_eventV4 = db_events_v4['eventV4']


# mail configure
mailto_list = ["1192309514@qq.com"]
mail_host = "smtp.126.com"
mail_user = "guangheauto"
mail_pass = "hello123"  # guanghedev
mail_postfix = "126.com"


def sendMail(toList, subject, content):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ";".join(toList)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user, mail_pass)
        s.sendmail(me, toList, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False


def post_man(mail_title, mail_log):
    mail_title = mail_title + " Count WARNING"
    try:
        if sendMail(mailto_list, mail_title, mail_log):
            print("[*] SEND SUCCESS title: %s") % (mail_title)
            sys.exit()
        else:
            print("[*] SEND FAILURE title: %s") % (mail_title)
    except Exception, e:
        print(str(e))
        raise


class get_collection_start_end_count(object):
    def __init__(self, arg):
        self.collecion_instance = arg

    def first_doc(self):
        collecion = self.collecion_instance
        return collecion.find_one({"serverTime":{"$exists": True}})

    def last_doc(self):
        collecion = self.collecion_instance
        return list(collecion.find({}).sort("_id", -1).limit(1))[0]

    def count_docs(self, start, end):
        collecion = self.collecion_instance
        return collecion.count({
            "serverTime": {
                "$gte": start,
                "$lte": end
            },
            "platform":{"$ne": "backend"}
        })


print("创建数据库实例")
eventV4_Obj = get_collection_start_end_count(collections_eventV4)


print("加载线上数据量count信息")
subprocess.Popen('scp master@bd.yangcong345.com:/Backup/v4_events_httplogs_orderstuff/monitor/onlineDbCount.json ./', stdout=subprocess.PIPE, shell=True)


online_info = {}
with open("./onlineDbCount.json", "r") as data_file:
    data = json.load(data_file)
    online_info["start"] = data["start"]
    online_info["end"] = data["end"]
    online_info["count"] = data["count"]


print("本地数据量count计算")
start = dateutil.parser.parse(online_info["start"])
end = dateutil.parser.parse(online_info["end"])
local_docs_count = eventV4_Obj.count_docs(start, end)


print("线上线下量级比对")
online_docs_count = online_info["count"]


BASE_DIFF_COUNT = 1000
diff_count = online_docs_count - local_docs_count
if abs(diff_count) >= BASE_DIFF_COUNT:
    print("线上线下数据量差距大于1000")
    warnning_info = ("online %s, offline %s, diff: %s")%(online_docs_count, local_docs_count, diff_count)
    print("Send WARNING MAIL")
    post_man("线上线下数据量差距大于1000", warnning_info)
else:
    print("线上 - 线下 数据量")
    print("online %s, offline %s, diff: %s")%(online_docs_count, local_docs_count, diff_count)
    # post_man("线上线下数据量差距大于1000", str(diff_count))
