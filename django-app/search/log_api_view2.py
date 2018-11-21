# coding:utf-8

## GB 国标要求的所有内容进行编写和上传

## 访问日志, 里面的相关设置根据各种 type 获取结果
from datetime import datetime, timedelta
from website.settings import LocalAccessLogTable
from wafmanage.permissions.plat_permissions import SecurityPermission

def get_jl_accsslog(
        type="remote_addr",
        accesslog_table="phaser1_apacheaccesslogdetail",
        start_time=None,
        end_time=None,
        limit=10,
        daysdelta=150, **kwargs,
       ):

    if not end_time:
        end_time = str(datetime.now()).split('.')[0]

    if not start_time:
        start_time = str(datetime.now() - timedelta(days=daysdelta)).split('.')[0]

    _types = ["request_method", "request_version",
              "request_url", "status", "device",
              "os", "user_agent", "remote_addr"]
    if type not in _types:
        return

    query_sql = """select {search_type}, count({search_type}) as c from (
select id, remote_addr, remote_user, time_local, 
  os, device, user_agent,status, substring_index(request, ' ', 1) as request_method,
   substring_index(substring_index(request, ' ', 2), '?', 1) as request_url,  
     substring_index(request, ' ', -1) as request_version, body_bytes_sent,       
         substring_index(http_referer, '?', 1) as http_referer
           from {accesslog_table} where time_local BETWEEN
            '{start_time}' and '{end_time}' ) as accesslog 
            group by {search_type} order by c desc limit {limit};""".format(
        search_type=type,
        accesslog_table=accesslog_table,
        limit=limit,
        start_time=start_time,
        end_time=end_time
    )
    # from wafmanage.utils.db_utils import from_sql_get_data

    return query_sql, _types
    ## 根据不同的参数类型进行聚类


## 统计最近 limit 天里面用户的字节数统计，用户的访问数统计
def tj_bytes_timedelta(limit_bytes=1024,
                       limit_vtimes=10,
                       remote_addrs=None,
                       split_type="date",
                       daysdelta=90,
                       start_time=None,
                       end_time=None,
                       accesslog_table="phaser1_apacheaccesslogdetail",
                       extra=None,
                       **kwargs):
    # _types_dict = dict(
    #     day="day",
    #     date="date",
    #     month="month",
    #     week="week",
    #     year="year",
    # )

    type = split_type
    if not end_time:
        end_time = str(datetime.now()).split('.')[0]

    if not start_time:
        start_time = str(datetime.now() - timedelta(days=daysdelta)).split('.')[0]

    remote_addr_partern = ""
    if remote_addrs:
        remote_addr_partern = "and remote_addr in ('"+ "', '".join(remote_addrs.replace(" ","").split(",")) + "') "

    extra_coditions = ""
    if extra:
        extra_coditions = " and lst={} ".format(extra)

    query_sql = """select * from (
    select remote_addr, lst, sum(body_bytes_sent) as count_bytes, count(remote_addr) as visit_times  from (
      select id, remote_addr, remote_user, time_local, {type}(time_local) as lst,
        os, device, user_agent,status, substring_index(request, ' ', 1) as request_method,
         substring_index(substring_index(request, ' ', 2), '?', 1) as request_url,  
         substring_index(request, ' ', -1) as request_version, body_bytes_sent,       
             substring_index(http_referer, '?', 1) as http_referer
               from {accesslog_table_name} where time_local BETWEEN
                '{start_time}' and '{end_time}' {remote_addr_partern}) as accesslog 
            group by remote_addr, lst order by lst desc, visit_times desc ) as local_t 
            where count_bytes > {limit_bytes} and visit_times > {limit_vtimes}  {extra_coditions};""".format(
        limit_bytes=limit_bytes,
        accesslog_table_name=accesslog_table,
        type=type,
        remote_addr_partern=remote_addr_partern,
        start_time=start_time,
        end_time=end_time,
        extra_coditions=extra_coditions,
        limit_vtimes =limit_vtimes,
    )
    return query_sql


from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

### 访问日志基础统计接口
@api_view(['POST'])
@permission_classes((IsAuthenticated, SecurityPermission))
def jla_search1(request):
    data = request.data

    instance = dict(
        type=data["type"] if "type" in data.keys() else "remote_addr",
        accesslog_table=LocalAccessLogTable,
        daysdelta=int(data["daysdelta"]) if "daysdelta" in data.keys() else 90,
        limit=int(data["limit"]) if "limit" in data.keys() else 100,
        start_time=data["start_time"] if "start_time" in data.keys() else None,
        end_time=data["end_time"] if "end_time" in data.keys() else None,
    )
    query_sql, _types = get_jl_accsslog(**instance)
    if instance["type"] not in _types:
        return Response({"stat": False}, {"reason":"输入类型错误"})
    # print(query_sql)
    from wafmanage.utils.db_utils import from_sql_get_data
    _objs = from_sql_get_data(query_sql)["data"]

    pager = int(data["page"]) if "page" in data.keys() else 1
    p = Paginator(_objs, 10)
    all_counts = p.count  # 对象总数
    page_count = p.num_pages  # 总页数
    pj = p.page(pager)
    objs = pj.object_list

    return Response(
        {"search_params": data, "res": objs, "page_count": page_count, "pager": pager, "all_counts": all_counts})


### 访问日志, 用户的访问次数接口
### 访问日志基础统计接口
@api_view(['POST'])
@permission_classes((IsAuthenticated, SecurityPermission))
def jla_search2(request):
    data = request.data

    instance = dict(
        limit_bytes=int(data["limit_bytes"]) if "limit_bytes" in data.keys() else 10240,
        limit_vtimes=int(data["limit_vtimes"]) if "limit_vtimes" in data.keys() else 10240,
        remote_addrs=data["remote_addrs"] if "remote_addrs" in data.keys() else None,
        split_type=data["split_type"] if "split_type" in data.keys() else None,

        accesslog_table=LocalAccessLogTable,

        daysdelta=int(data["daysdelta"]) if "daysdelta" in data.keys() else 90,
        limit=int(data["limit"]) if "limit" in data.keys() else 100,
        start_time=data["start_time"] if "start_time" in data.keys() else None,
        end_time=data["end_time"] if "end_time" in data.keys() else None,
        extra=data["extra"] if "extra" in data.keys() else None,
    )
    query_sql = tj_bytes_timedelta(**instance)

    from wafmanage.utils.db_utils import from_sql_get_data
    _objs = from_sql_get_data(query_sql)["data"]

    pager = int(data["page"]) if "page" in data.keys() else 1
    p = Paginator(_objs, 10)
    all_counts = p.count  # 对象总数
    page_count = p.num_pages  # 总页数
    pj = p.page(pager)
    objs = pj.object_list

    return Response(
        {"search_params": data, "res": objs, "page_count": page_count, "pager": pager, "all_counts": all_counts})



### 访问日志
@api_view(['POST'])
@permission_classes((IsAuthenticated, SecurityPermission))
def jls_search(request):
    data = request.data
    instance = dict(
        request_method=data["request_method"] if "request_method" in data.keys() else None,
        request_version=data["request_version"] if "request_version" in data.keys() else None,
        src_host=data["src_host"] if "src_host" in data.keys() else None,
        src_ip=data["src_ip"] if "src_ip" in data.keys() else None,
        request_url=data["request_url"] if "request_url" in data.keys() else None,
        category=data["category"] if "category" in data.keys() else None,  # 分类
        content_type=data["content_type"] if "content_type" in data.keys() else None,
        resp_code=int(data["resp_code"]) if "resp_code" in data.keys() else None,
        limit=int(data["limit"]) if "limit" in data.keys() else 100,
        start_time=data["start_time"] if "start_time" in data.keys() else None,
        end_time=data["end_time"] if "end_time" in data.keys() else None,
    )

    from wafmanage.utils.db_utils import from_sql_get_data
    from .seclog_search import seclog_search, seclog_search2
    _objs = from_sql_get_data(seclog_search2(**instance))["data"]
    # return Response(_objs)
    ### 开始准备分页

    pager = int(data["page"]) if "page" in data.keys() else 1
    p = Paginator(_objs, 10)
    all_counts = p.count  # 对象总数
    page_count = p.num_pages  # 总页数
    pj = p.page(pager)
    objs = pj.object_list

    return Response(
        {"search_params": data, "res": objs, "page_count": page_count, "pager": pager, "all_counts": all_counts})
