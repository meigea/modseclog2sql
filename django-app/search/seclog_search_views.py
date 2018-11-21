# coding:utf-8

from django.core.paginator import Paginator
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .seclog_search3 import seclog_search_jl, seclog_search3, seclog_search_condition, get_all_info_dependon_auditid

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def ip_attack_catecount_splitby_datetype(request):
    data = request.data
    instance = dict(
        src_ip=data["src_ip"] if "src_ip" in data.keys() else None,
        category=data["category"] if "category" in data.keys() else None,
        split_type=data["split_type"] if "split_type" in data.keys() else 'date',
        start_time=data["start_time"] if "start_time" in data.keys() else None,
        end_time=data["end_time"] if "end_time" in data.keys() else None,
    )
    from wafmanage.utils.db_utils import from_sql_get_data
    _objs = from_sql_get_data(seclog_search3(**instance))["data"]
    # return Response(_objs)
    ## 原来的版本就是直接获取的 _objs
    pager = int(data["page"]) if "page" in data.keys() else 1
    p = Paginator(_objs, 10)
    all_counts = p.count  # 对象总数
    page_count = p.num_pages  # 总页数
    pj = p.page(pager)
    objs = pj.object_list

    return Response(
        {"search_params": data, "res": objs, "page_count": page_count, "pager": pager, "all_counts": all_counts})


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def seclog_jl(request):
    data = request.data
    instance = dict(
        src_ip=data["src_ip"] if "src_ip" in data.keys() else None,
        category=data["category"] if "category" in data.keys() else None,
        split_type=data["split_type"] if "split_type" in data.keys() else 'date',
        start_time=data["start_time"] if "start_time" in data.keys() else None,
        end_time=data["end_time"] if "end_time" in data.keys() else None,
        jl_param=data["jl_param"] if "jl_param" in data.keys() else 'audit_date', ## 进行聚类的目标
        limit= int(data["limit"]) if "limit" in data.keys() else None,
    )
    from wafmanage.utils.db_utils import from_sql_get_data
    _objs = from_sql_get_data(seclog_search_jl(**instance))["data"]
    # return Response(_objs)
    ## 原来的版本就是直接获取的 _objs
    pager = int(data["page"]) if "page" in data.keys() else 1
    p = Paginator(_objs, 10)
    all_counts = p.count  # 对象总数
    page_count = p.num_pages  # 总页数
    pj = p.page(pager)
    objs = pj.object_list

    return Response(
        {"search_params": data, "res": objs, "page_count": page_count, "pager": pager, "all_counts": all_counts})


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def seclog_condition_search(request):
    data = request.data
    instance = dict(
        src_ip=data["src_ip"] if "src_ip" in data.keys() else None,
        category=data["category"] if "category" in data.keys() else None,
        split_type=data["split_type"] if "split_type" in data.keys() else 'date',
        start_time=data["start_time"] if "start_time" in data.keys() else None,
        end_time=data["end_time"] if "end_time" in data.keys() else None,
        # jl_param=data["jl_param"] if "jl_param" in data.keys() else 'audit_date', ## 进行聚类的目标
        limit= int(data["limit"]) if "limit" in data.keys() else None,
        audit_date_value=data["audit_date_value"] if "audit_date_value" in data.keys() else None, ## 聚类后的日期查看器
    )
    from wafmanage.utils.db_utils import from_sql_get_data
    _objs = from_sql_get_data(seclog_search_condition(**instance))["data"]
    # return Response(_objs)
    ## 原来的版本就是直接获取的 _objs
    pager = int(data["page"]) if "page" in data.keys() else 1
    p = Paginator(_objs, 10)
    all_counts = p.count  # 对象总数
    page_count = p.num_pages  # 总页数
    pj = p.page(pager)
    objs = pj.object_list

    return Response(
        {"search_params": data, "res": objs, "page_count": page_count, "pager": pager, "all_counts": all_counts})


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, ))
def seclog_detail_by_audlogid(request):
    data = request.GET if request.method == 'GET' else request.data
    audit_logid = data["audit_logid"]
    res_data = get_all_info_dependon_auditid(audit_logid=audit_logid)
    return Response({"datas": res_data})
