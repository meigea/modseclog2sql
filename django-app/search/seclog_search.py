# coding:utf-8

from datetime import datetime
search_params = """ id | logsize | http_user_agent | http_ver | src_host |\
  src_ip | waf_serv | audit_time | content_length | resp_code | uniq_id | request_url \
 | request_method | content_type """

extends_params = """ audit_logid | hid | matched_data |\
  rule_id | cn_msg| category """

import re

## 根据sql的字段, 得到字段
def get_sql_params_dps():
    # from wafmanage.utils.db_utils import from_sql_get_data
    #
    return ", ".join([re.match("\s+(.*?)\s+", x).group(1)
                      for x in search_params.split("|")
                        if re.match("\s+(.*?)\s+", x)])


def seclog_search(request_method=None,
                    src_host=None,
                    src_ip=None,
                    # remote_addr=None,
                    request_url=None,
                    request_version=None,
                    resp_code=None,
                    content_type=None,
                    start_time=None,
                    end_time=None,
                    category=None,
                    limit=20,
                  ):


    conditions = ""
    if request_method:
        request_method_partern = "'" + "', '".join(request_method.split(",")) + "'"
        conditions += "and request_method in ({}) ".format(request_method_partern)

    if request_version:
        request_version_partern = "'" + "','".join(request_version.split(",")) + "'"
        conditions += "and request_version in ({}) ".format(request_version_partern)

    if src_ip:
        conditions += "and src_ip in ({ips}) ".format(ips="'" + "','".join(src_ip.split(",")) + "'")

    if src_host:
        conditions += "and src_host in ({ips}) ".format(ips="'" + "','".join(src_host.split(",")) + "'")

    if request_url:
        conditions += "and request_url regexp '{}' ".format(request_url)

    if content_type:
        conditions += "and content_type = '{}' ".format(content_type)

    if resp_code:
        conditions += "and resp_code regexp '{}' ".format(int(resp_code))

    if start_time or end_time:
        if not start_time:
            start_time = "2017-3-15"
        if not end_time:
            end_time = str(datetime.now().date())

    conditions += "and audit_time between '{start_time}' and '{end_time}' ".format(
            start_time=start_time, end_time=end_time
        )
    ## 最近的条目
    conditions += "order by audit_time desc"

    cate_condition = ""
    if category:
        cate_condition = "having category = '{}'".format(category)

    query_sql = """select * from (select t4.*, modsechinfo.matched_data from (select audit_logid,any_value(cn_msg) as cn_msg, any_value(category), max(mc), any_value(hid) as hid from 
(select audit_logid, category, max(ccate) as mc, any_value(hid) as hid, any_value(cn_msg) as cn_msg from 
  (select audit_logid, count(category) as ccate, category, any_value(hid) as hid, any_value(cn_msg) as cn_msg from 
    (select c.*,ruletxt.cn_msg,ruletxt.category from 
          (select a11.*, modsechinfo.matched_data,modsechinfo.rule_id from 
            (select a1.*, b1.modseclogphaserhinfo_id as hid  from 
                (select * from modseclog where id >0 {conditions} order by audit_time) as a1
                 left join modseclog_hloginfo as b1
                on a1.id = b1.modseclogdetail_id) as a11 
                left join 
                modsechinfo
                on modsechinfo.id = a11.hid) as c 
                left join ruletxt
                on ruletxt.rule_id=c.rule_id) as main_t group by audit_logid, category {cate_condition}) 
                as tt2 group by audit_logid, category HAVING mc > 0) as tt3 group by audit_logid) as t4
                left join modsechinfo on modsechinfo.id = t4.hid ) as t5
                 left join modseclog on modseclog.audit_logid=t5.audit_logid where id > 0 """.format(
        conditions=conditions,
        cate_condition=cate_condition
    )

    ## 只要前面的几条数据
    query_sql += " limit {limit}".format(limit=limit)

    return query_sql + " ;"

def seclog_search2(TableName="modseclog",
                    request_method=None,
                    src_host=None,
                    src_ip=None,
                    # remote_addr=None,
                    request_url=None,
                    request_version=None,
                    resp_code=None,
                    content_type=None,
                    start_time=None,
                    end_time=None,
                    category=None,
                    limit=20,
                  ):


    conditions = ""
    if request_method:
        request_method_partern = "'" + "', '".join(request_method.split(",")) + "'"
        conditions += "and request_method in ({}) ".format(request_method_partern)

    if request_version:
        request_version_partern = "'" + "','".join(request_version.split(",")) + "'"
        conditions += "and request_version in ({}) ".format(request_version_partern)

    if src_ip:
        conditions += "and src_ip in ({ips}) ".format(ips="'" + "','".join(src_ip.split(",")) + "'")

    if src_host:
        conditions += "and src_host in ({ips}) ".format(ips="'" + "','".join(src_host.split(",")) + "'")

    if request_url:
        conditions += "and request_url regexp '{}' ".format(request_url)

    if content_type:
        conditions += "and content_type = '{}' ".format(content_type)

    if resp_code:
        conditions += "and resp_code = {} ".format(int(resp_code))

    if start_time or end_time:
        if not start_time:
            start_time = "2017-3-15"
        if not end_time:
            end_time = str(datetime.now().date())

    conditions += "and audit_time between '{start_time}' and '{end_time}' ".format(
            start_time=start_time, end_time=end_time
        )
    ## 最近的条目
    sql_orderby = "order by audit_time desc "

    cate_condition = ""
    cate_condition2 = ""
    if category:
        # cate_condition = "having cate_id in (select cate_id from rulecate where category='{}') ".format(category)
        cate_condition2 = "and category='{}' ".format(category)

    query_sql = """select {search_params} from (select tt4.*, modsechinfo.matched_data from 
	(select rulecate.category, t4.* from 
	 (select audit_logid, any_value(cate_id) as cate_id, max(ccate) as mc, any_value(hid) as hid, any_value(cn_msg) as cn_msg, any_value(rule_id) as m_rid from 
	  (select audit_logid, count(cate_id) as ccate, cate_id, any_value(hid) as hid, any_value(cn_msg) as cn_msg, any_value(rule_id) as rule_id from 
		(select c.*,ruletxt.cn_msg, if(isnull(ruletxt.cate_id), 404, ruletxt.cate_id) as cate_id from 
			  (select a11.*, modsechinfo.matched_data,modsechinfo.rule_id from 
				(select a1.*, b1.modseclogphaserhinfo_id as hid  from 
					(select * from modseclog where id >0 {conditions}  ) as a1
					 left join modseclog_hloginfo as b1
					on a1.id = b1.modseclogdetail_id) as a11 
					left join 
					modsechinfo
					on modsechinfo.id = a11.hid) as c 
					left join ruletxt
					on ruletxt.rule_id=c.rule_id) as main_t group by audit_logid, cate_id {cate_condition} )  as t2
				   group by audit_logid HAVING mc > 0) as t4 left join rulecate on rulecate.id=t4.cate_id) as tt4
					left join modsechinfo on modsechinfo.id = tt4.hid ) as t5
					 left join modseclog on modseclog.audit_logid=t5.audit_logid where id > 0 {cate_condition2}""".format(
        conditions=conditions,
        cate_condition=cate_condition,
        cate_condition2=cate_condition2,
        search_params="request_method, m_rid, src_host, src_ip, category, cn_msg, content_type, audit_time, matched_data, \
        substring_index(substring_index(substring_index(request_url,' ', -2), ' ', 1), '?', 1) as request_url, resp_code, t5.audit_logid "
    )

    ## 只要前面的几条数据
    query_sql += sql_orderby
    query_sql += " limit {limit}".format(limit=limit)

    return query_sql + " ;"





