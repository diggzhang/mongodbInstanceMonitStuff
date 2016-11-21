# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
from datetime import datetime
import datetime
import json
from StringIO import StringIO
import time
from datetime import date


db_host = MongoClient("10.8.8.111", 27017)
db_events_v35 = db_host["eventsV35"]
db_events_v4 = db_host["eventsV4"]


collections_event_v32 = db_events_v35['eventV32']
collections_event_v35 = db_events_v35['eventV35']


collections_getMeProfileLogs = db_events_v4['getMeProfileLogs']
collections_orderEvents = db_events_v4['orderEvents']
collections_eventV4 = db_events_v4['eventV4']


def docs_counter(collecion):
    num_of_doc = collecion.count()
    return num_of_doc


collecion_list = {
    "eventsV32": collections_event_v32,
    "eventsV35": collections_event_v35,
    "eventV4": collections_eventV4,
    "orderEvents": collections_orderEvents,
    "getMeProfileLogs":collections_getMeProfileLogs
}


all_collections_status = []
for collecion in collecion_list:
    this_dict = {"genre": collecion, "sold": 0}
    this_dict["sold"] = collecion_list[collecion].count()
    all_collections_status.append(this_dict)


with open("./dbCountData.json", "w") as outfile:
    json.dump(all_collections_status, outfile)


daily_data = []
with open("./eventv4DailyCount.json", "r") as data_file:
    data = list(json.load(data_file))
    new_daily_eventv4_count = {"date": date.today().strftime("%Y%m%d"), "count": collections_eventV4.count()}
    data.append(new_daily_eventv4_count)
    daily_data = data


with open("./eventv4DailyCount.json", "w") as outfile:
    json.dump(daily_data, outfile)
