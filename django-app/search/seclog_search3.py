from datetime import datetime, timedelta


def seclog_search3(src_ip=None,
                    start_time=None,
                    end_time=None,
                    category=None,
                    split_type='date',**kwargs
                  ):
    conditions = ""

    if src_ip:
        conditions += "and src_ip in ({ips}) ".format(ips="'" + "','".join(src_ip.split(",")) + "'")

    if start_time or end_time:
        if not start_time:
            start_time = "2018-10-1"
        if not end_time:
            end_time = str(datetime.now().date())

    conditions += "and audit_time between '{start_time}' and '{end_time}' ".format(
            start_time=start_time, end_time=end_time
        )

    cate_condition2 = ""

    if category:
        # cate_condition = "having cate_id in (select cate_id from rulecate where category='{}') ".format(category)
        cate_condition2 = "and category='{}' ".format(category)

    query_sql = """select src_ip, audit_date, count(category) as count_cate, category, max(audit_time) as last_audtime from (select {search_params} from (select tt4.*, modsechinfo.matched_data from 
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
					on ruletxt.rule_id=c.rule_id) as main_t group by audit_logid, cate_id )  as t2
				   group by audit_logid HAVING mc > 0) as t4 left join rulecate on rulecate.id=t4.cate_id) as tt4
					left join modsechinfo on modsechinfo.id = tt4.hid ) as t5
					 left join modseclog on modseclog.audit_logid=t5.audit_logid where id > 0 {cate_condition2}) as sect group by src_ip, audit_date, category order by audit_date desc, src_ip  """.format(
        conditions=conditions,
        cate_condition2=cate_condition2,
        search_params="src_ip, category, audit_time, {split_type}(audit_time) as audit_date ".format(split_type=split_type)
    )

    return query_sql + " ;"

def seclog_search_jl(src_ip=None,
                    start_time=None,
                    end_time=None,
                    category=None,
                    split_type="date",
                    jl_param='category',
                    limit=None, **kwargs
                  ):
    conditions = ""

    if src_ip:
        conditions += "and src_ip in ({ips}) ".format(ips="'" + "','".join(src_ip.split(",")) + "'")

    if start_time or end_time:
        if not start_time:
            start_time = str((datetime.now() -timedelta(days=7)).date() )
        if not end_time:
            end_time = str(datetime.now().date())
    conditions += "and audit_time between '{start_time}' and '{end_time}' ".format(
            start_time=start_time, end_time=end_time
        )

    cate_condition2 = ""

    if category:
        # cate_condition = "having cate_id in (select cate_id from rulecate where category='{}') ".format(category)
        cate_condition2 = "and category='{}' ".format(category)

    sql_query = lambda param:"""select count({param}) as cop, {param}  from (select {search_params} from (select tt4.*, modsechinfo.matched_data from 
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
    					on ruletxt.rule_id=c.rule_id) as main_t group by audit_logid, cate_id )  as t2
    				   group by audit_logid HAVING mc > 0) as t4 left join rulecate on rulecate.id=t4.cate_id) as tt4
    					left join modsechinfo on modsechinfo.id = tt4.hid ) as t5
    					 left join modseclog on modseclog.audit_logid=t5.audit_logid where id > 0 {cate_condition2}) as sect 
    					 group by {param} order by cop desc""".format(
        conditions=conditions,
        cate_condition2=cate_condition2,
        param=param,
        search_params="src_ip, category, audit_time, {split_type}(audit_time) as audit_date ".format(split_type=split_type)
    )
    ## 规定时间内; 每天的次数, 类别的数量, IP的数量等
    query_sql = sql_query(jl_param)

    if limit:
        try:
            query_sql += " limit {} ".format(int(limit))
        except:
            pass

    query_sql += ";"
    return query_sql


def seclog_search_condition(src_ip=None,
                    start_time=None,
                    end_time=None,
                    category=None,
                    split_type="date",
                    limit=None,
                    audit_date_value='2018-10-16',**kwargs
                  ):
    conditions = ""

    if src_ip:
        conditions += "and src_ip in ({ips}) ".format(ips="'" + "','".join(src_ip.split(",")) + "'")

    if start_time or end_time:
        if not start_time:
            start_time = str( ( datetime.now() - timedelta(days=7) ).date() )
        if not end_time:
            end_time = str( datetime.now().date() )
    conditions += "and audit_time between '{start_time}' and '{end_time}' ".format(
            start_time=start_time, end_time=end_time
        )

    cate_condition2 = ""

    if category:
        # cate_condition = "having cate_id in (select cate_id from rulecate where category='{}') ".format(category)
        cate_condition2 = "and category='{}' ".format(category)

    query_sql = """select * from (select {search_params} from (select tt4.*, modsechinfo.matched_data from 
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
    					on ruletxt.rule_id=c.rule_id) as main_t group by audit_logid, cate_id )  as t2
    				   group by audit_logid HAVING mc > 0) as t4 left join rulecate on rulecate.id=t4.cate_id) as tt4
    					left join modsechinfo on modsechinfo.id = tt4.hid ) as t5
    					 left join modseclog on modseclog.audit_logid=t5.audit_logid where id > 0 {cate_condition2}) as sect """.format(
        conditions=conditions,
        cate_condition2=cate_condition2,
        search_params="t5.*, {split_type}(audit_time) as audit_date, src_ip, audit_time ".format(split_type=split_type)
    )

    if audit_date_value:
        if split_type == 'date':
            query_sql += " where audit_date = '{}' ".format(audit_date_value)
        else:
            try:
                query_sql += " where audit_date = {} ".format(audit_date_value)
            except:
                pass
    if limit:
        try:
            query_sql += " limit {} ".format(int(limit))
        except:
            pass

    query_sql += ";"
    return query_sql


from django.forms.models import model_to_dict
def get_all_info_dependon_auditid(audit_logid):
    from phaser1.models import ModsecLogDetail
    datas = ModsecLogDetail.objects.filter(audit_logid=audit_logid)
    resp_data = []
    for x in datas:
        data = model_to_dict(x)
        data["hloginfo"] = [model_to_dict(y) for y in x.hloginfo.all()]
        resp_data.append(data)
    return resp_data




