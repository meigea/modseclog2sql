# coding:utf-8
from utils.dt_tool import get_ua_and_os_from_User_Agent
from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogSaveTableName, ModSecLogSaveTableName, SysLogFilterParten
from utils.mongo import MongoConn

MPConn = MongoConn(SysLogMongoDBConfig)

def get_detailed_modseclog_info():
    for x in MPConn.db[ModSecLogSaveTableName].find(projection={"_id": False}):
        print(x)

