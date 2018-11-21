# coding:utf-8
from utils.mongo import MongoConn
from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogDir, \
    AccessLogSaveTableName, OpreationLogCollectionName, CentureAccessLogManager
from logConfig import logging

import pymongo
from datetime import datetime
## 记录所有的操作过程的日志

def put_opt(counts, line=0, filename=AccessLogDir, collection_name=AccessLogSaveTableName):
    ## 插入记录
    params = dict(
        time=datetime.now(), ## 这个地方有缺陷,
        # 应该再增加一个日期进来。date
        filepath=filename,
        line=line,
        collection_name= collection_name,
        counts= counts
    )
    content = "在【"+str(params["time"])+"】读取"+filename+\
              "文件`向"+ collection_name +"`中插入了[ " + str(counts) + " ]条目"
    logging.info(content)
    params.setdefault("content", content)
    collection = MongoConn(SysLogMongoDBConfig).db[OpreationLogCollectionName]
    collection.insert(params)


def show_opts():
    collection = MongoConn(SysLogMongoDBConfig).db[OpreationLogCollectionName]
    return collection.find(projection={"_id": False})


def get_line():
    try:
        # data = collection.find(projection={"_id": False}).sort([("time", pymongo.DESCENDING), ])[0]
        # if data["time"].date() < datetime.now().date():
        #     return 0
        # 如果今天MongoDb中没有写入任何数据, 说明前面的日志都是错误的; 删除已经读取的记录行
        collection = MongoConn(SysLogMongoDBConfig).db[OpreationLogCollectionName]
        data = collection.find(projection = {"_id": False})
        today_accsslog_counts = 0
        for x in data:
            if x["time"].date() == datetime.now().date():
                today_accsslog_counts += x["counts"]
        if today_accsslog_counts == 0:
            remove_today_writelogs()
            return 0
        return data["line"]
    except:
        return 0

# 升级版; 有文件识别的功能; 如果读取不同的文件, 行数恢复
def get_line_afile(filename=AccessLogDir):
    try:
        data = collection.find({"filepath": filename}, projection = {"_id": False}).sort([("time", pymongo.DESCENDING), ])

        today_accsslog_counts = 0
        for x in data:
            if x["time"].date() == datetime.now().date():
                today_accsslog_counts += x["counts"]

        if today_accsslog_counts == 0:
            remove_today_writelogs()
            return 0
        collection = MongoConn(SysLogMongoDBConfig).db[OpreationLogCollectionName]
        newer = collection.find({"filepath": filename}, projection = {"_id": False}).sort([("time", pymongo.DESCENDING), ])[0]
        return newer["line"]
    except:
        return 0

def remove_today_writelogs():
    from logConfig import logging
    logging.warn("今日初始化 `accesss_log` 的所有访问日志 ")
    collection = MongoConn(SysLogMongoDBConfig).db[OpreationLogCollectionName]
    data = collection.find().sort([("time", pymongo.DESCENDING), ])[0]
    if str(data["time"].date()) == str(datetime.now().date()):
        collection.remove({"_id": data["_id"]})
    # MongoConn(SysLogMongoDBConfig).db[CentureAccessLogManager].remove()



