# coding:utf-8

from django.core.paginator import Paginator

# from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from website.settings import LocalAccessLogTable

SEARCH_CONDOTION_TABLE_NAME = "search_condition"

def get_local_db():
    from phaser1.apscheduler.utils.mongo import MongoConn
    from phaser1.apscheduler.config import WafMongoConfig
    ldc = WafMongoConfig.copy()
    ldc["db_name"] = "waf"
    return MongoConn(ldc).db[SEARCH_CONDOTION_TABLE_NAME]

def get_data_from_sqls(key, limit=15):
    from wafmanage.utils.db_utils import from_sql_get_data

    return [x[key] for x in from_sql_get_data("""select {key}, count({key}) as c from {table} group by {key} order by c desc limit {limit};""".format(
        table=LocalAccessLogTable, limit=limit, key=key) )["data"] ]


def get_default_conditions():
    from httputils.models import RequestMethod, HttpVersion
    from phaser1.models import RuleTxt2, RuleCate
    return dict(
        # content_types=get_data_from_sqls("content_type", limit=15),
        os=get_data_from_sqls("os", limit=15),
        device = get_data_from_sqls("device", limit=15),
        user_agent = get_data_from_sqls("user_agent", limit=15),
        status = get_data_from_sqls("status", limit=15),
        remote_addr = get_data_from_sqls("remote_addr", limit=15),
        request_version = [x.http_version_name for x in HttpVersion.objects.all()],
        category=[x.category for x in RuleCate.objects.all()],
        request_method = [x.request_method for x in RequestMethod.objects.filter(is_common=True)],
    )



@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def set_common_conditions(request):
    ## 后台管理接口
    from datetime import datetime
    _now = datetime.now()
    init_user = request.user.username if request.user else "bug001"
    get_local_db().insert({"conditions": get_default_conditions(), "add_dt": _now, "add_user": init_user})

    return Response({"stat": True, "reason": "已经添加最新的条件记录到Mongo数据库中"})


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_common_conditions(request):
    import pymongo
    data = get_local_db().find(projection={"_id": False}).sort([("add_dt", pymongo.DESCENDING), ])[0]
    return Response(data)


def demo():

    temp = {
        "os":"操作系统",
        "remote_addr":"访客IP",
        "device":"设备",
        "user_agent":"客户端",
        "request_method":"请求方法",
        "request_version":"协议版本",
        "category":"告警类别",
        "http_referer":"来源URL",
        "time_local":"访问时间",
        "request_url":"请求URL",
        "content_type":"请求内容类型",
        "src_host":"访客源",
        "resp_code":"状态码",
        "status":"状态码",
        "audit_time":"访问时间",
        "limit":"限制条目",
        "is_ignore_static":"无视静态文件",
        "limit_static":"仅要静态文件",
        "cn_msg":"告警消息",
    }
