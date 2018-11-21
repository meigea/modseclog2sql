from config import common_config


def get_config_filestr(config):
    import os
    local_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(local_dir, "crs-setup.conf.abstract") , "r+", encoding="utf-8") as fr:
        frstr = fr.read()
        fr.close()
    return frstr.format(**config)


# 将配置写入 `mongo` 中。
def write_to_wafconfig(config, table="common_config", desc="ModifyCommon"):
    from utils.mongo import MongoConn
    from config import MongoConfig
    from datetime import datetime
    prefix_insert = dict(
        modify_dt=str(datetime.now()),
        desc=desc
    )
    prefix_insert.setdefault(table, config)
    ## 这个集合只存一条记录。
    MongoConn(MongoConfig).db[table].remove()
    MongoConn(MongoConfig).db[table].insert(prefix_insert)
    return dict(
        done=True,
        dt=str(datetime.now()),
        desc=desc,
        table=table,
        db=MongoConfig["db_name"]
    )


## 将当前修改的文本写入到文档中; 如果没有文本写入基础配置。
def get_filestr_dependson_config(config=common_config, intodb=True):
    import os
    BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FilesDir = os.path.join(BaseDir, "files")

    with open(os.path.join(FilesDir, "crs-setup.conf.abstract"), "r+", encoding="utf-8") as fr:
        frstr = fr.read()
        fr.close()
    filestr = frstr.format(**config)
    if intodb:
        from datetime import datetime
        from utils.mongo import MongoConn
        from config import MongoConfig
        MongoConn(MongoConfig).db["files"].remove()
        MongoConn(MongoConfig).db["files"].insert(dict(
            current_filestr=filestr,
            modfiyuser="system",
            modify_date=str(datetime.now()),
        ))
        # 执行结束; 返回整个文本
    return filestr, True


def init_config(self_config=common_config, type="modify"):
    # from config import common_config
    from opt.config_partern import write_to_wafconfig
    if type == "init":
        write_to_wafconfig(common_config, table="init_config", desc="InitCRSconf")
    write_to_wafconfig(own_config, table="common_config", desc="ModifyCommon")

    from opt.config_partern import write_to_wafconfig, get_filestr_dependson_config
    return get_filestr_dependson_config(config=self_config)[1]

# if __name__ == '__main__':
#     write_to_mongodb()
