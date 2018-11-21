from utils.dt_tool import get_ua_and_os_from_User_Agent

from syslog.conf.configs import SysLogMongoDBConfig, \
    AccessLogSaveTableName, ModSecLogSaveTableName, SysLogFilterParten
from utils.mongo import MongoConn
from logConfig import logging


MPConn = MongoConn(SysLogMongoDBConfig)

##### 访问日志和告警日志的格式化; 通过产生。
class GetDetailedLog():
    def __init__(self, save=True, show=False):
        self.save = save
        self.show = show

    ## 弃用; 已经放在了syslog/main的里面
    def get_accesslog(self):
        accesslogs = []
        for item in MPConn.db[AccessLogSaveTableName].find(projection={"_id": False}):
            temp_dict = item.copy()
            http_user_agent = item["http_user_agent"]
            http_user_agent_detailed_info = get_ua_and_os_from_User_Agent(http_user_agent)
            new_item = dict(temp_dict, **http_user_agent_detailed_info)
            accesslogs.append(new_item)
        logging.info("执行写入访问日志详细概况")
        if self.save:
            MPConn.db[AccessLogSaveTableName + "_detailed"].insert(accesslogs)
        if self.show:
            for x in MPConn.db[AccessLogSaveTableName + "_detailed"].find(projection={"_id": False}):
                print(x)

    def get_modseclog(self):
        logging.info("2.1：执行写入告警日志详细概况")
        if self.save:
            ## 保存只跟这个有关
            from opt.wt_parse import init_auditlog_detailed, remove_alldata_modsecdetailed
            # remove_alldata_modsecdetailed() # 开始有问题的时候执行
            modseclog_detailed = init_auditlog_detailed()
            if modseclog_detailed:
                MPConn.db[ModSecLogSaveTableName + "_detailed"].insert(modseclog_detailed)
        if self.show:
            for x in MPConn.db[ModSecLogSaveTableName + "_detailed"].find(projection={"_id": False}):
                print(x)

## 测试环境
def test():
    # GetDetailedLog(save=False, show=True).get_accesslog()
    GetDetailedLog(save=True, show=True).get_modseclog()

## 生产环境下
def detailed_work():
    logging.info("2.0：执行写入详细日志脚本开始")
    # GetDetailedLog(save=True, show=False).get_accesslog()
    GetDetailedLog(save=True, show=False).get_modseclog()
    logging.info("2.2：执行写入详细日志脚本成功")


