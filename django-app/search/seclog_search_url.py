from django.conf.urls import url, include

from .seclog_search_views import ip_attack_catecount_splitby_datetype , \
    seclog_jl, seclog_condition_search, seclog_detail_by_audlogid

seclog_search_urlparterns = [
    # url(r'^accsslog_search', include(accs_router.urls)),
    url(r'^ip_attack_catecount_splitby_datetype', ip_attack_catecount_splitby_datetype),
    url(r'^seclog_jl', seclog_jl),
    url(r'^seclog_condition_search', seclog_condition_search),
    url(r'^seclog_detail_by_audlogid', seclog_detail_by_audlogid),
]