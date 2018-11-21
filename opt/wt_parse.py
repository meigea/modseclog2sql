# coding:utf-8
import re

from utils.dt_tool import get_pydt_based_logdt
### 获取 H 阶段的日志处理相关的事情和日志相关的内容;
### 下面这个函数是设置的 Demo 文本。
def get_h_logfile_demo():
    import os
    BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FilesDir = os.path.join(BaseDir, "files")

    with open(os.path.join(FilesDir, "modlogh.example.txt"), "r+", encoding="utf-8") as fr:
        frstr = fr.read()
        fr.close()
    SPLIT_KEY = "JtsdWwdzZbx"
    new_str = frstr.replace("ModSecurity: ", SPLIT_KEY + "ModSecurity: ")
    res_dict_array = []
    for x in new_str.split(SPLIT_KEY):
        if "ModSecurity" in x:
            prefix_partern = re.match("(ModSecurity: .*)\[file.*", x).group(1)
            prefix_len = len(prefix_partern)
            features = re.findall("""\[(\w+)\s"(.*?)"\]""", x[prefix_len:])
            alert_dct = {}
            alert_dct.setdefault("tag", [])

            for (key, value) in features:
                if key == "tag":
                    alert_dct[key].append(value)
                    continue
                alert_dct.setdefault(key, value)

            res_dict_array.append(alert_dct)
    return res_dict_array

## 审计日志头
def modsec_Alog_extract(content_str):
    matched1 = re.match("\[(.*?) \+0800\] (.*?) (.*?) (\d+) (.*?) (\d+).*?", content_str)
    ## 这个位置谨防告警日期格式存在其他情况; 后续再增加正则匹配
    if matched1:
        res = dict(
            audit_time = get_pydt_based_logdt(matched1.group(1)),
            uniq_id = matched1.group(2),
            src_ip = matched1.group(3),
            logsize = matched1.group(4),
            src_host = matched1.group(5),
            server_port = matched1.group(6),
        )
        return res
    return {}


def modsec_Blog_extract(content_str):
    http_user_agent_matd = re.match("([A-Z]+)\s(.*?)(HTTP.*?)\n.*", content_str)
    hua_matd = re.findall(".*?\nUser-Agent: (.*?)\n.*", content_str)

    request_header_infos = {"http_user_agent": ""}
    if hua_matd:
        request_header_infos["http_user_agent"] = hua_matd[0]
    if http_user_agent_matd:
        request_header_infos1 = dict(
            request_method=http_user_agent_matd.group(1),
            request_url=http_user_agent_matd.group(2),
            http_ver = http_user_agent_matd.group(3)
        )
        res = dict(request_header_infos, **request_header_infos1)
        return res
    return {}

## 响应信息
def modsec_Flog_extract(content_str):
    response_header_infos = {}
    matd1 = re.match(".*?(HTTP.*?)\s(\d+)\n", content_str)
    matd2 = re.findall(".*?Server:\s(.*?)\n", content_str)
    matd3 = re.findall(".*?Content-Type:\s(.*?)\n", content_str)
    matd4 = re.findall(".*?Content-Length:\s(\d+)\n", content_str)
    if matd1:
        response_header_infos.setdefault("http_ver", matd1.group(1))
        response_header_infos.setdefault("resp_code", matd1.group(2))
    if matd2:
        response_header_infos.setdefault("waf_serv", matd2[0])
    if matd3:
        response_header_infos.setdefault("content_type", matd3[0])
    if matd4:
        response_header_infos.setdefault("content_length", matd4[0])

    return response_header_infos


### H 阶段的 Log 函数；服务于后面的所有
def modsec_Hlog_extract(frstr):
    SPLIT_KEY = "JtsdWwdzZbx"
    new_str = frstr.replace("ModSecurity: ", SPLIT_KEY + "ModSecurity: ")
    res_dict_array = []
    for x in new_str.split(SPLIT_KEY):
        if "ModSecurity" in x:
            prefix_partern = re.match("(ModSecurity: .*)\[file.*", x).group(1)
            prefix_len = len(prefix_partern)
            features = re.findall("""\[(\w+)\s"(.*?)"\]""", x[prefix_len:])
            alert_dct = {}
            alert_dct.setdefault("tag", [])

            for (key, value) in features:
                if key == "tag":
                    alert_dct[key].append(value)
                    continue
                alert_dct.setdefault(key, value)
            # res_dict_array.append(alert_dct)
            res_dict_array.append(dict(
                rule_id = alert_dct["id"],
                matched_data = alert_dct["data"] if "data" in alert_dct.keys() else "",
                msg = alert_dct["msg"] if "msg" in alert_dct.keys() else "",
            ))
    return {"hloginfo": res_dict_array}

from opt.detailedlog.accesslog_detailed import MPConn, ModSecLogSaveTableName
## 将已经细化后的条目的ID进行删除。
def get_all_auditlog_id():
    auditlog_ids = set([x["audit_logid"] for x in MPConn.db[ModSecLogSaveTableName].find(projection={"_id": False})])
    auditlogd_ids = set([x["audit_logid"] for x in MPConn.db[ModSecLogSaveTableName+"_detailed"].find(projection={"_id": False})])
    return auditlog_ids - auditlogd_ids

def convert_aitemlog_to_wedetailed(audit_logid, audit_logid_datas=None):
    if not audit_logid_datas:
        audit_logid_datas = [x for x in MPConn.db[ModSecLogSaveTableName].find({"audit_logid": audit_logid},
                                                                     projection={"_id": False})]
    temp = {"audit_logid": audit_logid}
    for x in audit_logid_datas:
        # exec("""temp = dict(temp, **modsec_"""+ x["auditlog_signal"] +"""log_extract(x["auditlog_content"]))""")
        if x["auditlog_signal"] == "A":
            temp = dict(temp, **modsec_Alog_extract(x["auditlog_content"]))
        if x["auditlog_signal"] == "B":
            temp = dict(temp, **modsec_Blog_extract(x["auditlog_content"]))
        if x["auditlog_signal"] == "F":
            temp = dict(temp, **modsec_Flog_extract(x["auditlog_content"]))
        if x["auditlog_signal"] == "H":
            temp = dict(temp, **modsec_Hlog_extract(x["auditlog_content"]))
    return temp

def init_auditlog_detailed():
    audit_detailed_items = []
    need_detaild_ids = get_all_auditlog_id()
    for audit_logid in need_detaild_ids:
        audit_detailed_items.append(convert_aitemlog_to_wedetailed(audit_logid=audit_logid))
    return audit_detailed_items
    # MPConn.db[ModSecLogSaveTableName + "_detailed"].insert(audit_detailed_items)

def remove_alldata_modsecdetailed():
    MPConn.db[ModSecLogSaveTableName+"_detailed"].remove()

def test():
    print(init_auditlog_detailed())




