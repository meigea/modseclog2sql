# coding:utf-8

SysLogMongoDBConfig = dict(
    host="127.0.0.1",
    port=27017,
    db_name='syslog',
    username=None,
    password=None
 )

MongoRuleConfig = dict(
    host="127.0.0.1",
    port=27017,
    db_name='waf_rules',
    username=None,
    password=None
)

AccessLogSaveTableName = "accesslog"
ModSecLogSaveTableName = "modseclog"

## 2018-10-10 修改; 单机部署修改
AccessLogDir = "/spool/vhost/logs/"
ModsecLogPath = "/var/log/modsec_audit.log"

# if SysLogHost == "192.168.1.233":
#     AccessLogDir = "/home/syslog/log/nginx/access.log"
#     ModsecLogDir = "/home/syslog/log/modsec_audit.log"

WhiteLogHostList = ['127.0.0.1', "waf.test.com"]

## 测试环境中
import sys
import os
if sys.platform == 'win32':
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # LOG_DIR = os.path.join(BASE_DIR, "test", "log")

    ## 下面两个才是需要用到的变量
    # AccessLogDir = os.path.join(LOG_DIR, "access.log")
    AccessLogDir = "A:\\1\\demo"
    ModsecLogPath = os.path.join("A:\\1\\demo", "modsec_audit.log")