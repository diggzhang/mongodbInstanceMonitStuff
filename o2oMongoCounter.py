# -*- coding: utf-8 -*-
"""
线上写一个脚本，拿到eventv4的第一条数据的时间 as online_start_time
拿到当前最后一条的数据的servertime as online_end_time
以start_time和end_time为range做一次count as count
生成json文件 {"start_time":ISODate() , "end_time":ISODate（）,count: INT_number} --> onlineCount.json
/Backup/v4_events_httplogs_orderstuff/monitor/onlineDbCount.json  o2oMongoCounter.py
done
线下scp onlineCount.json
一个脚本取到start_time,end_time,排除后端埋点情况下做local_count，
local_count - count 看值
如果值特别大，发邮件报警
"""

import pymongo
from pymongo import MongoClient
from datetime import datetime
import datetime
import json
from StringIO import StringIO
import time
from datetime import date
import calendar


CONN_ADDR1 = 'dds-xxxxxxxxxxxxxxxxx.mongodb.com:3717'
CONN_ADDR2 = 'dds-xxxxxxxxxxxxxxxxx.mongodb.com:3717'
REPLICAT_SET = 'mgset-11'
username = 'xxXXXxxx'
password = '234411xxxxxxxxxxxx'


# TODO: 配置成线上可用的Client配置
db_host = MongoClient([CONN_ADDR1, CONN_ADDR2], replicaSet=REPLICAT_SET)
db_host.admin.authenticate(username, password)
db_events_v4 = db_host["events"]
collections_eventV4 = db_events_v4['eventv4']


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
            }
        })


json_raw_info = {}


print("create instance ...")
eventV4_Obj = get_collection_start_end_count(collections_eventV4)


print("get first doc serverTime")
online_first_doc_servertime = eventV4_Obj.first_doc()['serverTime']
json_raw_info["start"] = online_first_doc_servertime


print("get last doc serverTime")
online_last_doc_servertime = eventV4_Obj.last_doc()['serverTime']
json_raw_info["end"] = online_last_doc_servertime


print online_first_doc_servertime, online_last_doc_servertime
print("count all docs")
docs_count = eventV4_Obj.count_docs(online_first_doc_servertime, online_last_doc_servertime)
json_raw_info["count"] = docs_count


json_raw_info["start"] = calendar.timegm(json_raw_info["start"].timetuple())
json_raw_info["end"] = calendar.timegm(json_raw_info["end"].timetuple())


print json_raw_info


with open("./onlineDbCount.json", "w+") as outfile:
    json.dump(json_raw_info, outfile)
