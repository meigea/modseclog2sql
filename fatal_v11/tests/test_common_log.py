# coding:utf-8
from fatal_v11.scripts.get_common_logs import TxTCommonLog


def test_accesslog_getting():
    datas, line = TxTCommonLog(filename="A:\\1\\temp2\\waf.access_20181101.log").get_access_logs3()
    for x in datas:
        print(x)


def test_auditlog_getting():
    datas = TxTCommonLog(filename="A:\\1\\temp2\\modsec_audit_20181026.log").modseclog_to_detaild()
    for x in datas:
        print(x)








