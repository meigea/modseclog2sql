import re

from utils.mongo import MongoConn
from utils.dt_tool import get_ua_and_os_from_User_Agent
from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogDir, ModsecLogDir, \
    AccessLogSaveTableName, ModSecLogSaveTableName, SysLogFilterParten

from syslog.script.opreation.opt import get_line, put_opt, show_opts, get_line_afile
from logConfig import logging

MPConn = MongoConn(SysLogMongoDBConfig)

class InitLogs():
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

    def get_access_logs2(self):
        # from syslog.script.opreation.opt import get_line, put_opt
        current_line = get_line_afile(self.filename) if self.AccessLogRecode else 0# 每天中获取最近的一次读取的行数。
        line_index = 0
        lines = []
        with open(self.filename, "r", encoding="utf-8") as f:
            temp_lines = f.readlines() # 整个文本的所有行
            for line in temp_lines:
                if line_index < current_line:
                    continue
                line_index += 1
                import re
                matched = re.match(SysLogFilterParten + "(.*)", line)
                if matched:
                    lines.append(matched.group(1))
            f.close()

        res = []
        for line in lines:
            import re
            partern = '(.*?)\s-\s(.*?)\s\[(.*?)\]\s\"(.*?)\"\s(.*?)\s(.*?)\s\"(.*?)\"\s\"(.*?)\"\s\"(.*)\"'
            temp = re.findall(partern, line.split("\n")[0])
            remote_addr, remote_user, time_local, request, status, body_bytes_sent, \
            http_referer, http_user_agent, http_x_forwarded_for = tuple(temp[0])
            res_dic = dict(
                remote_addr=remote_addr,
                remote_user=remote_user,
                time_local=time_local,
                request=request,
                status=status,
                body_bytes_sent=body_bytes_sent,
                http_user_agent=http_user_agent,
                # http_x_forwarded_for=http_x_forwarded_for,
                http_referer=http_referer,
            )
            new_item = res_dic
            ## 直接生成详细的访问日志。原本是直接字典
            if self.detailed:
                http_user_agent_detailed_info = get_ua_and_os_from_User_Agent(http_user_agent)
                new_item = dict(res_dic, **http_user_agent_detailed_info)
            res.append(new_item)

        return res, len(temp_lines)

    def get_access_logs(self):
        # from syslog.script.opreation.opt import get_line, put_opt
        current_line = get_line_afile(self.filename) if self.AccessLogRecode else 0 # 每天中获取最近的一次读取的行数。
        line_index = 0
        lines = []

        with open(self.filename, "r", encoding="utf-8") as f:
            temp_lines = f.readlines() # 整个文本的所有行
            for line in temp_lines:
                if line_index < current_line:
                    continue
                line_index += 1
                import re
                matched = re.match(SysLogFilterParten + "(.*)", line)
                if matched:
                    lines.append(matched.group(1))
            f.close()
        # 先去掉`syslog`的发送日志头标识, 接下来才是常规的流程。

        res = []
        for line in lines:
            import re
            partern = '(.*?)\s-\s(.*?)\s\[(.*?)\]\s\"(.*?)\"\s(\d+)\s(\d+)\s\"(.*?)\"\s\"(.*?)\"'
            # partern = '(.*?)\s-\s(.*?)\s\[(.*?)\]\s\"(.*?)\"\s(\d+)\s(\d+)\s\"(.*?)\"\s\"(.*?)\"\n'
            temp = re.match(partern, line)
            if temp:
                temp_array = tuple([temp.group(i + 1) for i in range(8)])
                remote_addr, remote_user, time_local, request, status, body_bytes_sent, \
                http_referer, http_user_agent = temp_array
                res_dic = dict(
                    remote_addr=remote_addr,
                    remote_user=remote_user,
                    time_local=time_local,
                    request=request,
                    status=status,
                    body_bytes_sent=body_bytes_sent,
                    http_user_agent=http_user_agent,
                    # http_x_forwarded_for=http_x_forwarded_for,
                    http_referer=http_referer,
                )
                # res.append(res_dic)
                new_item = res_dic
                ## 直接生成详细的访问日志。原本是直接字典
                if self.detailed:
                    http_user_agent_detailed_info = get_ua_and_os_from_User_Agent(http_user_agent)
                    new_item = dict(res_dic, **http_user_agent_detailed_info)
                res.append(new_item)

        return res, len(temp_lines)

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

def init_auditlog(filename=ModsecLogDir):
    # 这里的 AccessLogRecode 是启用多个文件扫描
    res = InitLogs(filename=filename, AccessLogRecode=True).get_auditlogs()
    # 无重复插入
    MPConn.insert_data_uniq(ModSecLogSaveTableName, res)
    logging.info("1.2：入库告警日志")

def init_accesslog(filename=AccessLogDir):
    res, line = InitLogs(filename=filename, AccessLogRecode=True).get_access_logs()
    logging.info("1.1：入库访问日志记录【" + filename + "】第 " + str(line) + " 行")
    ## AccessLog 的日志最终存储到Mysql的过程中再去重
    put_opt(len(res), line=line)  # 存储最新读取文本行记录的位置
    MPConn.insert_data(AccessLogSaveTableName, res)

def init_accesslog1015(filename=AccessLogDir):
    res, line = InitLogs(filename=filename, AccessLogRecode=True).get_access_logs3()
    logging.info("1.1：入库访问日志记录【" + filename + "】第 " + str(line) + " 行")
    put_opt(len(res), line=line)  # 存储最新读取文本行记录的位置
    # print(res)
    # MPConn.insert_data(AccessLogSaveTableName, res)
    MPConn.insert_data_uniq(AccessLogSaveTableName, res, key="request_id")

    #show_access_logdata()
# def test_show_datas():
#     for x in MPConn.db[ModSecLogSaveTableName].find({"auditlog_signal": "A"}, {"auditlog_content": 0}):
#         print(x)
#

def show_access_logdata():
    for x in MPConn.db[AccessLogSaveTableName].find():
        print(x)
#
# def delete_accesslog_collection():
#     MPConn.db[AccessLogSaveTableName].remove()
#
# def delete_modseclog_collection():
#     MPConn.db[ModSecLogSaveTableName].remove()
#
# def remove_action_log_today():
#     from syslog.script.opreation.opt import remove_today_writelogs
#     remove_today_writelogs()

## 生产环境
def work(Debug=False):
    if Debug:
        from syslog.init import initial_all_collections
        initial_all_collections()
    logging.warn("=========日志导入和初始化阶段开始========")
    logging.info("1.0：【Start】两种日志直接入Mongo库")
    init_accesslog()
    init_auditlog()
    logging.info("1.3：【End】两种日志直接入Mongo库")

    ## 开始对告警日志进行细化
    from opt.detailedlog.accesslog_detailed import detailed_work
    detailed_work()

    ## 执行存入Mysql的记录
    from opt.detailedlog.mlog_to_sql import LogToSql
    LogToSql().accesslog_to_sql()

    LogToSql().modseclog_to_sql()
    logging.warn("=========日志导入结束========")

# 和上面相比较， 这个有指定路径的
def kacfun(acceelog_filepath=AccessLogDir, modseclog_filepath=ModSecLogSaveTableName):
    logging.info("1.0：【Start】两种日志直接入Mongo库")
    init_accesslog(filename=acceelog_filepath)
    init_auditlog(filename=modseclog_filepath)
    logging.info("1.3：【End】两种日志直接入Mongo库")
    ## 开始对告警日志进行细化
    from opt.detailedlog.accesslog_detailed import detailed_work
    detailed_work()
    ## 执行存入Mysql的记录
    from opt.detailedlog.mlog_to_sql import log_to_sql
    log_to_sql()












