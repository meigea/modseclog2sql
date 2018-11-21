# coding:utf-8
import re

# from utils.mongo import MongoConn
from utils.dt_tool import get_ua_and_os_from_User_Agent
from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogDir, ModsecLogDir, \
    AccessLogSaveTableName, ModSecLogSaveTableName, SysLogFilterParten

from opt.wt_parse import convert_aitemlog_to_wedetailed

# from syslog.script.opreation.opt import get_line, put_opt, show_opts, get_line_afile
from logConfig import logging

# MPConn = MongoConn(SysLogMongoDBConfig)

class TxTCommonLog():
    def __init__(self, filename=None, AccessLogRecode=True, detailed=True):
        self.AccessLogRecode = AccessLogRecode
        self.detailed = detailed
        if filename:
            self.filename = filename
        else:
            # self.filename = "./kdata/modsec_audit.log"
            self.filename = "/var/log/waf_log/modsec_audit.log"

    def get_auditlogs(self):
        lines = []
        with open(self.filename, "r", encoding="utf-8") as f:
            temp_lines = f.readlines()
            for line in temp_lines:
                matched = re.match(SysLogFilterParten + "(.*)", line)
                if matched:
                    # lines.append(matched.group(1))
                    lines.append(matched.group(1) + "\n")
            f.close()
        res = []
        partern = "---(.*?)---(.*?)--.*"
        middle_content = ""
        temp_auditlog_id, temp_auditlog_signal, temp_auditlog_startline, auditlog_endline = "","","",""
        for line_index in range(len(lines)):
            data = re.match(partern, lines[line_index])
            if data:
                if(middle_content == ""):
                    # 第一次进来了但是已经收集了中间的数据
                    temp_auditlog_id = data.group(1)
                    temp_auditlog_signal = data.group(2)
                    temp_auditlog_startline = line_index
                else:
                    # 第二次进来了但是已经收集了中间的数据
                    temp_auditlog_endline = line_index - 1
                    res.append(dict(
                        audit_logid=temp_auditlog_id,
                        auditlog_signal=temp_auditlog_signal,
                        auditlog_startline=temp_auditlog_startline,
                        auditlog_endline=temp_auditlog_endline,
                        auditlog_content=middle_content,
                        ))
                    # 收集完了就把这个中间内容集合置为空
                    middle_content = ""
                    data = re.match(partern, lines[line_index])
                    temp_auditlog_id = data.group(1)
                    temp_auditlog_signal = data.group(2)
                    temp_auditlog_startline = line_index
                continue

            middle_content += lines[line_index]
        # 结束了最后一行要加上自己的内容
        res.append(dict(
            audit_logid=temp_auditlog_id,
            auditlog_signal=temp_auditlog_signal,
            auditlog_startline=temp_auditlog_startline,
            auditlog_endline=temp_auditlog_startline,
            auditlog_content="",
        ))
        return res

    def modseclog_to_detaild(self):
        modsec_txtlogs = self.get_auditlogs()
        ## 建立一个键值队的集合，一个键key（audit_logid） 对应一个关于它自己的列表
        _modsec_txtlog_dict = {}
        for x in modsec_txtlogs:
            if "audit_logid" in x.keys():
                if x["audit_logid"] in _modsec_txtlog_dict.keys():
                    _modsec_txtlog_dict[x["audit_logid"]].append(x)
                else:
                    ## 注意这里是把这个audit_logid作为字符串的键值对的`键`
                    _modsec_txtlog_dict[x["audit_logid"]] = [x]
            else:
                logging.debug("ERROR-NO-AuditLogId!")
        modsec_detailed_logs = []
        for key, values in _modsec_txtlog_dict.items():
            modsec_detailed_logs.append(convert_aitemlog_to_wedetailed( audit_logid=key, audit_logid_datas=values ))

        return modsec_detailed_logs

    def get_access_logs3(self):
        lines = []
        with open(self.filename, "r", encoding="utf-8") as f:
            temp_lines = f.readlines() # 整个文本的所有行
            for line in temp_lines:
                matched = re.match(SysLogFilterParten + "(.*)", line)
                if matched:
                    lines.append(matched.group(1))
            f.close()
        # 先去掉`syslog`的发送日志头标识, 接下来才是常规的流程。
        res = []
        for line in lines:
            ## nginx 新的 partern 模式
            # partern = '(.*?)\s-\s(.*?)\s\[(.*?)\]\s\"(.*?)\"\s(\d+)\s(\d+)\s\"(.*?)\"\s\"(.*?)\"'
            # partern = '(.*?)\s-\s(.*?)\s\[(.*?)\]\s\"(.*?)\"\s(\d+)\s(\d+)\s\"(.*?)\"\s\"(.*?)\"\n'
            partern = '(.*?)\s-\s(.*?)\s\[(.*?)\]\s\"(.*?)\"\s(\d+)\s(\d+)\s\"(.*?)\"\s\"(.*?)\"\s\"(.*?)\"\s([a-zA-Z0-9]+)'
            temp = re.match(partern, line)
            if temp:
                temp_array = tuple([temp.group(i + 1) for i in range(10)])
                remote_addr, remote_user, time_local, request, status, body_bytes_sent, \
                http_referer, http_user_agent, http_x_forwarded_for, request_id = temp_array
                res_dic = dict(
                    remote_addr=remote_addr,
                    remote_user=remote_user,
                    time_local=time_local,
                    request=request,
                    status=status,
                    body_bytes_sent=body_bytes_sent,
                    http_user_agent=http_user_agent,
                    http_x_forwarded_for=http_x_forwarded_for,
                    http_referer=http_referer,
                    request_id=request_id,
                )
                # res.append(res_dic)
                new_item = res_dic
                ## 直接生成详细的访问日志。原本是直接字典
                if self.detailed:
                    http_user_agent_detailed_info = get_ua_and_os_from_User_Agent(http_user_agent)
                    new_item = dict(res_dic, **http_user_agent_detailed_info)
                res.append(new_item)

        return res, len(temp_lines)

