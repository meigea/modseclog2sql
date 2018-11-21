# coding:utf-8
from utils.dt_tool import get_pydt_based_logdt
from utils.django_module import django_setup
from utils.mongo import MongoConn
from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogSaveTableName, ModSecLogSaveTableName, CentureAccessLogManager
from logConfig import logging

import re

class LogToSql():
    def __init__(self, MongoConfig=SysLogMongoDBConfig, save=True):
        self.db = MongoConn(MongoConfig).db
        self.save=save

    def django_setup(self):
        # 开启Django服务
        django_setup()

    def accesslog_to_sql(self):
        from utils.django_module import django_setup
        django_setup()
        na_lists = []
        from phaser1.models import NginxAccessLogDetail
        # NginxAccessLogDetail.objects.all().delete()
        from datetime import datetime
        from wafmanage.utils.db_utils import from_sql_get_data
        today_date = str(datetime.now().date())
        try:
            # query_sql = "select request_id from accesslog where date(time_local) = '{today_date}'".format(today_date=today_date)
            query_sql = "select request_id from accesslog;"
            have_into_mysql_ids = [x["request_id"] for x in from_sql_get_data(query_sql)["data"] ]
            # print(from_sql_get_data(query_sql)["data"] )
            # print(have_into_mysql_ids)
        except:
            have_into_mysql_ids = []

        for x in self.db[AccessLogSaveTableName].find():
            obj = x.copy()
            del obj["_id"]
            if obj["request_id"] in have_into_mysql_ids:
                continue
            try:
                obj["time_local"] = get_pydt_based_logdt(re.match("(.*?)\s(.*)", obj["time_local"]).group(1))
            except:
                # print(re.match("(.*?)\s(.*)", obj["time_local"]).group(1))
                logging.warn("Error:存在AccessLog日志不一样的正则 " + obj["time_local"])
                return
            ## 记录这些条目已经存储进了 Mysql
            na_lists.append(NginxAccessLogDetail(**obj))

        if na_lists:
            NginxAccessLogDetail.objects.bulk_create(na_lists)
        logging.info("3.0: 写入【"+str(len(na_lists))+"】条访问日志到MYSQL数据库")
        #print("3.0: 写入【"+ str(len(na_lists)) +"】条访问日志到MYSQL数据库")

    def modseclog_to_sql(self):
        from utils.django_module import django_setup
        django_setup()
        from datetime import datetime
        default_time = datetime(1900, 8, 14)
        from phaser1.models import ModsecLogDetail, ModSecLogPhaserHinfo

        write_counts = 0 ## 记录写入的数值
        for x in self.db[ModSecLogSaveTableName + "_detailed"].find(projection={"_id": False}):
            if len(ModsecLogDetail.objects.filter(audit_logid=x["audit_logid"]))>0:
                continue
            item = ModsecLogDetail()
            item.logsize = int(x["logsize"]) if "logsize" in x.keys() else 0
            item.audit_logid = x["audit_logid"] if "audit_logid" in x.keys() else ""
            item.http_user_agent = x["http_user_agent"] if "http_user_agent" in x.keys() else ""
            item.http_ver = x["http_ver"] if "http_ver" in x.keys() else ""
            item.src_host = x["src_host"] if "src_host" in x.keys() else ""
            item.src_ip = x["src_ip"] if "src_ip" in x.keys() else ""
            item.waf_serv = x["waf_serv"] if "waf_serv" in x.keys() else ""
            item.audit_time = x["audit_time"] if "audit_time" in x.keys() else default_time
            item.content_length = int(x["content_length"]) if "content_length" in x.keys() else 0
            item.resp_code = int(x["resp_code"]) if "resp_code" in x.keys() else 0
            item.uniq_id = x["uniq_id"] if "uniq_id" in x.keys() else ""
            item.request_url = x["request_url"][:253] if "request_url" in x.keys() else ""
            item.request_method = x["request_method"] if "request_method" in x.keys() else ""
            item.content_type = x["content_type"]  if "content_type" in x.keys() else ""
            item.save()
            if "hloginfo" in x.keys():
                for y in x["hloginfo"]:
                    hlogitem = ModSecLogPhaserHinfo.objects.create(**dict(
                        rule_id=int(y["rule_id"]) if "rule_id" in y.keys() else 0,
                        matched_data=y["matched_data"] if "matched_data" in y.keys() else "",
                        msg=y["msg"][:225] if "msg" in y.keys() else ""
                    ))
                    item.hloginfo.add(hlogitem)
            write_counts += 1
        logging.info("3.1-写入【"+str(write_counts)+"】条告警日志进入Mysql成功")
        #print("3.1-写入【"+str(write_counts)+"】条告警日志进入Mysql成功")


def log_to_sql():
    LogToSql().accesslog_to_sql()
    LogToSql().modseclog_to_sql()


