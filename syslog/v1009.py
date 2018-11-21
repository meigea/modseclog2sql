from logConfig import logging



def log_as1():
    from syslog.main import init_accesslog
    from opt.detailedlog.mlog_to_sql import LogToSql
    # logging.warn("=========日志导入和初始化阶段开始========")
    logging.info("#访问日志#【Start】 入Mongo库")
    init_accesslog()
    logging.info("#访问日志#【END】 入Mongo库")
    logging.info("#访问日志#【Start】 入MySql库")
    LogToSql().accesslog_to_sql()
    logging.info("#访问日志#【END】 入MySql库")



def log_ss2():
    from syslog.main import init_auditlog
    from opt.detailedlog.accesslog_detailed import detailed_work
    from opt.detailedlog.mlog_to_sql import LogToSql
    # logging.warn("=========日志导入和初始化阶段开始========")
    # logging.info("#访问日志#【Start】 入Mongo库")
    # init_accesslog()
    # logging.info("#访问日志#【END】 入Mongo库")
    # logging.info("#访问日志#【Start】 入MySql库")
    # LogToSql().accesslog_to_sql()
    # logging.info("#访问日志#【END】 入MySql库")
    # logging.info("#告警日志#【Start】 入Mongo库")
    logging.info("#告警日志#【Start】 入Mongo库")
    init_auditlog()
    logging.info("#告警日志#【Middle】重写详情入Mongo库")
    detailed_work()
    logging.info("#告警日志#【END】 入Mongo库")
    logging.info("#告警日志#【END】 入MySql库")
    LogToSql().modseclog_to_sql()
    logging.info("#告警日志#【END】 入MySql库")
    # logging.warn("=========日志导入阶段结束========")


def log_v1009():
    log_as1()
    log_ss2()


