from fatal_v11.tests.test_common_log import test_accesslog_getting, test_auditlog_getting
from fatal_v11.tests.test_common_log_to_db import test_accesslog_2_mysql, test_modseclog_2_mysql, test_accesslog_2_mongo, test_modseclog_2_mongo

from fatal_v11.v11 import sql_log
from logConfig import logging

if __name__ == '__main__':
    # test_accesslog_getting()
    # test_auditlog_getting()
    # test_modseclog_2_mysql()
    # test_accesslog_2_mongo()
    # test_modseclog_2_mongo()
    sql_log()
    logging.warn("【apscheduler】执行日志写入Mysql数据库成功")



