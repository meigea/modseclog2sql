import re
from utils.mongo import MongoConn
from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogDir, ModsecLogDir, \
    AccessLogSaveTableName, ModSecLogSaveTableName, SysLogFilterParten


MPConn = MongoConn(SysLogMongoDBConfig)

class InitAuditLogs():
    def __init__(self, filename=None):
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
                    lines.append(matched.group(1)+"\n")
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

    def get_access_logs(self):
        lines = []
        with open(self.filename, "r", encoding="utf-8") as f:
            temp_lines = f.readlines()
            for line in temp_lines:
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
                http_x_forwarded_for=http_x_forwarded_for,
                http_referer=http_referer,
            )
            res.append(res_dic)
        return res

def init_auditlog():
    res = InitAuditLogs(ModsecLogDir).get_auditlogs()
    ## 无重复插入
    MPConn.insert_data_uniq(ModSecLogSaveTableName, res)

def init_accesslog():
    res = InitAuditLogs(AccessLogDir).get_access_logs()
    ## AccessLog 的日志最终存储到Mysql的过程中再去重
    MPConn.insert_data(AccessLogSaveTableName, res)

def delete_modsec_log():
    MPConn.db[ModSecLogSaveTableName].remove()

def test_show_datas():
    for x in MPConn.db[ModSecLogSaveTableName].find({"auditlog_signal": "A"}, {"auditlog_content": 0}):
        print(x)

def show_access_logdata():
    for x in MPConn.db[AccessLogSaveTableName].find():
        print(x)


def test_demo():
    # delete_modsec_log()
    init_auditlog()
    init_accesslog()
    test_show_datas()
    show_access_logdata()
    MPConn.show_actions()


