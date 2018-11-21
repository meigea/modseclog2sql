# coding:utf-8
import sys
import re
from utils.mongo import MongoConn
from fatal_v11.cfg import ModSecLogSaveTableName, AccessLogSaveTableName, SysLogMongoDBConfig
from logConfig import logging

from fatal_v11.scripts.get_common_logs import TxTCommonLog

class LogToMongo():
    def __init__(self, save=True, filename="localhost-80.access.log", MAX_INSERT_NUM=200):
        self.save=save
        self.filename=filename
        try:
            self.server_port = re.match(".*\-(\d+)\.\w+\.log", str(filename).split("/")[-1]).group(1)
            if sys.platform == "win32":
                self.server_port = re.match(".*\-(\d+)\.\w+\.log",str(filename).split("\\")[-1]).group(1)
        except:
            logging.warn("SERVER_PORT_PARSE_ERROR")
            self.server_port = 80

    def get_latest_accsslog(self):
        datas, line = TxTCommonLog(filename=self.filename).get_access_logs3()
        return datas

    def get_latest_modseclog(self):
        return TxTCommonLog(filename=self.filename).modseclog_to_detaild()

    def accesslog_to_mongo(self):
        MongoConn(SysLogMongoDBConfig).insert_data_uniq(AccessLogSaveTableName, self.get_latest_accsslog(), key="request_id")
        # logging.warn()

    def modseclog_to_mongo(self):
        MongoConn(SysLogMongoDBConfig).insert_data_uniq(ModSecLogSaveTableName, self.get_latest_modseclog(),)






