from fatal_v11.scripts.log_to_mysql import LogToSql
from fatal_v11.scripts.log_to_mongo import LogToMongo
from fatal_v11.cfg import AccessLogDir, ModsecLogPath, WhiteLogHostList

import os
import re

def init_sql_db():
    LogToSql().init_sql_logdb()
    print("初始化SQL-Log-DB完成")

def write_accesslog():
    for path in os.listdir(AccessLogDir):
        if re.match("(.*)\-(\d+)\.access\.log", path):
            host = re.match("(.*)\-(\d+)\.access\.log", path).group(1)
            if host in WhiteLogHostList:
                continue
            LogToSql(filename=os.path.join(AccessLogDir, path)).accesslog_to_sql()
    print("Access写入Mysql")

def write_modseclog():
    LogToSql(filename=ModsecLogPath).modseclog_to_sql()
    print("Modsec写入Mysql")

def accesslog_backup2mongo():
    for path in os.listdir(AccessLogDir):
        if re.match("(.*)\-(\d+)\.access\.log", path):
            host = re.match("(.*)\-(\d+)\.access\.log", path).group(1)
            if host in WhiteLogHostList:
                continue
            LogToMongo(filename=os.path.join(AccessLogDir, path)).accesslog_to_mongo()
    print("Access写入Mongo")

def modsec_backup2mongo():
    LogToMongo(filename=ModsecLogPath).modseclog_to_mongo()
    print("Modsec写入Mongo")

def sql_log():
    # init_sql_db()
    write_accesslog()
    write_modseclog()

def mongo_log():
    modsec_backup2mongo()
    accesslog_backup2mongo()
