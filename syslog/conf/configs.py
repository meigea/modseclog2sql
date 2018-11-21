from syslog.conf import SysLogHost

SysLogMongoDBConfig = dict(
    host=SysLogHost,
    port=27017,
    db_name='syslog',
    username=None,
    password=None
 )

MongoRuleConfig = dict(
    host=SysLogHost,
    port=27017,
    db_name='waf_rules',
    username=None,
    password=None
)

## 特殊标记; 有可能是域名也可能是local host; syslog 的发送方IP
locate_fix = "localhost|syslog\.kac\.fun"
## Syslog-Ng 传递过程中增加的时间戳IP的格式
SysLogFilterParten = "\w+\s+\d+\s\d+:\d+:\d+\s("+ locate_fix +"|\d+\.\d+\.\d+\.\d+)\s"
####### 单机版本, 本机无视日志发送头的字符串 ############
if SysLogHost=="localhost":
    SysLogFilterParten = ""


# 每一个 MongoDB 都修改对应的日志存储为小的分集合。
from datetime import datetime
DateStramp = "_" + str(datetime.now().date()).replace("-","")


AccessLogSaveTableName = "accesslog" + DateStramp
ModSecLogSaveTableName = "modseclog"+ DateStramp
## 这两个都是辅助用的集合
CentureAccessLogManager = "accesslog_to_sql"  ## 记录MongoDB存储的访问日志进SQL库
OpreationLogCollectionName = "opt" ## 记录accesslog日志读取文件行

# AccessLogDir = "/var/log/waf_logs/nginx/access.log"
# ModsecLogDir = "/var/log/waf_logs/modsec_audit.log"

## 2018-10-10 修改; 单机部署修改
AccessLogDir = "/var/log/nginx/waf.access.log"
ModsecLogDir = "/var/log/modsec_audit.log"

# if SysLogHost == "192.168.1.233":
#     AccessLogDir = "/home/syslog/log/nginx/access.log"
#     ModsecLogDir = "/home/syslog/log/modsec_audit.log"

## 测试环境中
import sys
import os
if sys.platform == 'win32':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, "test", "log")

    ## 下面两个才是需要用到的变量
    # AccessLogDir = os.path.join(LOG_DIR, "access.log")
    AccessLogDir = os.path.join(LOG_DIR, "waf.access.log")
    ModsecLogDir = os.path.join(LOG_DIR, "modsec_audit.log")