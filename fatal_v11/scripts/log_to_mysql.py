# coding:utf-8
import sys
import re
from utils.dt_tool import get_pydt_based_logdt
from utils.django_module import django_setup
from logConfig import logging

from fatal_v11.scripts.get_common_logs import TxTCommonLog


class LogToSql():
    def __init__(self, filename="localhost-80.access.log", MAX_INSERT_NUM=200):
        self.filename=filename
        try:
            self.server_port = re.match(".*\-(\d+)\.\w+\.log", str(filename).split("/")[-1]).group(1)
            if sys.platform == "win32":
                self.server_port = re.match(".*\-(\d+)\.\w+\.log",str(filename).split("\\")[-1]).group(1)
        except:
            logging.warn("SERVER_PORT_PARSE_ERROR")
            self.server_port = 80

        self.MAX_INSERT_NUM=MAX_INSERT_NUM

    def django_setup(self):
        # 开启Django服务
        django_setup()

    def init_sql_logdb(self):
        self.django_setup()
        from phaser1.models import NginxAccessLogDetail, ModsecLogDetail
        NginxAccessLogDetail.objects.all().delete()
        ModsecLogDetail.objects.all().delete()

    def add_server_host_2dit(self, data):
        data["server_port"] = self.server_port if "server_port" not in data.keys() else 80
        return data

    def get_latest_accsslog(self):
        datas, line = TxTCommonLog(filename=self.filename).get_access_logs3()
        return datas

    def get_latest_modseclog(self):
        return TxTCommonLog(filename=self.filename).modseclog_to_detaild()

    def many_insert2_accesslog(self, nad_datas):
        self.django_setup()
        from phaser1.models import NginxAccessLogDetail
        from django.core.paginator import Paginator
        p = Paginator(nad_datas, self.MAX_INSERT_NUM) # 分页列别
        page_count = p.num_pages  # 总页数
        seccess_insert_num = 0
        # NginxAccessLogDetail.objects.all().delete()
        for x in [x+1 for x in range(page_count)]:
            nad_list = list(p.page(x).object_list)
            try:
                NginxAccessLogDetail.objects.bulk_create([NginxAccessLogDetail(**x) for x in nad_list])
                seccess_insert_num += self.MAX_INSERT_NUM
            except:
                for nad in nad_list:
                    try:
                        NginxAccessLogDetail.objects.create(**nad)
                        seccess_insert_num += 1
                    except:
                        pass
                        ## 这里处理效率较低;后期优化 // 重复返回错误
        return seccess_insert_num


    def accesslog_to_sql(self):
        self.django_setup()
        from phaser1.models import NginxAccessLogDetail
        nad_datas = []
        have_saved_reqids = [nad.request_id for nad in NginxAccessLogDetail.objects.all()]
        for x in [y for y in self.get_latest_accsslog() if y["request_id"] \
                not in have_saved_reqids]:
            obj = x.copy()
            try:
                obj["time_local"] = get_pydt_based_logdt(re.match("(.*?)\s(.*)", obj["time_local"]).group(1))
            except:
                # print(re.match("(.*?)\s(.*)", obj["time_local"]).group(1))
                logging.warn("Error:存在AccessLog日志不一样的正则 " + obj["time_local"])
                continue
            obj["server_port"] = self.server_port if "server_port" not in obj.keys() else 443
            nad_datas.append(obj)
        seccess_insert_num = self.many_insert2_accesslog(nad_datas)
        logging.info("插入【" + str(seccess_insert_num)  +"】条新数据到访问日志SQL数据库成功")

    def modseclog_to_sql(self):
        from utils.django_module import django_setup
        django_setup()
        from datetime import datetime
        default_time = datetime(1995, 8, 14)
        from phaser1.models import ModsecLogDetail, ModSecLogPhaserHinfo
        have_saved_audit_logid = [x.audit_logid for x in ModsecLogDetail.objects.all()]
        write_counts = 0 ## 记录写入的数值
        for x in self.get_latest_modseclog():
            ## 新增对象不可能存在重复; 所以把去重判别放在上面了
            if x["audit_logid"] in have_saved_audit_logid:
                continue
            item = ModsecLogDetail()
            item.logsize = int(x["logsize"]) if "logsize" in x.keys() else 0
            item.audit_logid = x["audit_logid"] if "audit_logid" in x.keys() else ""
            item.http_user_agent = x["http_user_agent"] if "http_user_agent" in x.keys() else ""
            item.http_ver = x["http_ver"] if "http_ver" in x.keys() else ""
            item.src_host = x["src_host"] if "src_host" in x.keys() else ""
            item.src_ip = x["src_ip"] if "src_ip" in x.keys() else ""
            item.server_port = x["server_port"] if "server_port" in x.keys() else "" # 2018-11-16 add port
            item.waf_serv = x["waf_serv"] if "waf_serv" in x.keys() else ""
            item.audit_time = x["audit_time"] if "audit_time" in x.keys() else default_time
            item.content_length = int(x["content_length"]) if "content_length" in x.keys() else 0
            item.resp_code = int(x["resp_code"]) if "resp_code" in x.keys() else 0
            item.uniq_id = x["uniq_id"] if "uniq_id" in x.keys() else ""

            item.request_url = x["request_url"][:253] if "request_url" in x.keys() else ""
            item.request_method = x["request_method"] if "request_method" in x.keys() else ""
            item.content_type = x["content_type"]  if "content_type" in x.keys() else ""

            item.server_port = x["server_port"] if "server_port" in x.keys() else self.server_port
            try:
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
            except:
                logging.info("该对象已存在")
        logging.info("写入【"+str(write_counts)+"】条告警日志进入Mysql成功")
        #print("3.1-写入【"+str(write_counts)+"】条告警日志进入Mysql成功")



