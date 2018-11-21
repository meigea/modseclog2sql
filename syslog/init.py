from utils.mongo import MongoConn
from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogSaveTableName, ModSecLogSaveTableName, \
    SysLogFilterParten, CentureAccessLogManager, OpreationLogCollectionName
from logConfig import logging


db = MongoConn(SysLogMongoDBConfig).db
def initial_all_collections(Sec=False, Ace=False):

    if Ace:
        db[AccessLogSaveTableName].remove()
        ## 实际上下面两个表在 2018-10-15 后已经失去了作用
        db[CentureAccessLogManager].remove()
        db[OpreationLogCollectionName].remove()
    if Sec:
        db[ModSecLogSaveTableName].remove()
        db[ModSecLogSaveTableName+"_detailed"].remove()

    from utils.django_module import django_setup
    django_setup()
    from phaser1.models import NginxAccessLogDetail, ModsecLogDetail, ModSecLogPhaserHinfo
    if Ace:
        NginxAccessLogDetail.objects.all().delete()
    if Sec:
        ModsecLogDetail.objects.all().delete()
        ModSecLogPhaserHinfo.objects.all().delete()

    logging.info("0：初始化所有的日志集合成功！")

