from config import common_config

import os
APS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELS_DIR = os.path.join(APS_DIR, "files")
CrsConfigSave = os.path.join(FIELS_DIR, "CrsSetupConfigs")

def get_config_filestr(this_config):
    with open(os.path.join(FIELS_DIR, "crs-setup.conf.abstract") , "r+", encoding="utf-8") as fr:
        frstr = fr.read()
        fr.close()
    return frstr.format(**this_config)

def write_into_dbconfigs():
    ## 从 configDb 取出来最新的config;
    from utils.mongo import MongoConn
    from config import CrsSetupMongoConfig, SetupConfigDictTableName
    import pymysql
    local_config = MongoConn(CrsSetupMongoConfig).db[SetupConfigDictTableName].find().sort([("_id", pymongo.DESCENDING)])[0]
    return local_config


def write_to_local_files(config_get=common_config, filew=True):
    from utils.mongo import MongoConn
    from config import CrsSetupMongoConfig, SetupConfigTableName
    from datetime import datetime

    current_time = str(datetime.now())
    file_uniq = current_time.replace(":", "").replace("-", "").replace(" ","")

    file_path = os.path.abspath(os.path.join(CrsConfigSave, "crs-setup-"+file_uniq+".conf"))

    result = dict(
        crs_setup_conf=get_config_filestr(config_get),
        file_path=file_path,
        done=False,
        dt=str(datetime.now()),
        table=SetupConfigTableName,
        db_config=CrsSetupMongoConfig,
        local_file=file_path
    )

    if filew:
        with open(result["local_file"], "w+", encoding="utf-8") as f:
            f.write(str(result["crs_setup_conf"]))
            f.close()
        result["done"] = True
    try:
        data = MongoConn(CrsSetupMongoConfig).db[SetupConfigTableName].insert(result)
        return dict(resp=data, stat=True)
    except:
        return dict(resp=result, stat=False)


########
# 弃用 #
#######