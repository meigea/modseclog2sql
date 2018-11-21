from django.conf.urls import url, include

from .log_api_views import  accsslog_search, seclog_search

logsearch_urlparterns = [
    # url(r'^accsslog_search', include(accs_router.urls)),
    url(r'^as', accsslog_search),
    url(r'^ss', seclog_search),
]

from .log_api_view2 import jla_search1, jla_search2
logsearch_urlparterns.extend([
    # url(r'^accsslog_search', include(accs_router.urls)),
    url(r'^get_jl_accsslog', jla_search1),
    url(r'^tj_bytes_timedelta', jla_search2),
])

from .condition_veiws import get_common_conditions, set_common_conditions
logsearch_urlparterns.extend([
    # url(r'^accsslog_search', include(accs_router.urls)),
    url(r'^get_common_conditions', get_common_conditions),
    url(r'^set_common_conditions', set_common_conditions),
])
# verdant-descent-220202|xx-net-to-gae-383941|xx-net-to-gae-38356|xx-net-to-gae-28257|xx-net-to-gae-38357|xx-net-to-gae-28258|xx-net-to-gae-28256|xx-net-to-gae-28259|xx-net-to-gae-383942|xx-net-to-gae-50001|xx-net-to-gae-50002|xx-net-to-gae-50003|xx-net-to-gae-50004|xx-net-to-gae-500014|xx-net-to-gae-50005|xx-net-to-gae-50006|xx-net-to-gae-50007|xx-net-to-gae-50008|xx-net-to-gae-50009|xx-net-to-gae-500010|xx-net-to-gae-500011|xx-net-to-gae-10000|xx-net-to-gae-10001|xx-net-to-gae-10002|xx-net-to-gae-10003|xx-net-to-gae-10004|xx-net-to-gae-10005|xx-net-to-gae-10006|xx-net-to-gae-10007|xx-net-to-gae-10008|xx-net-to-gae-10009|xxnet-to-gae-2000|xxnet-to-gae-20000|xxnet-to-gae-20001|xxnet-to-gae-20002|xxnet-to-gae-20004|xxnet-to-gae-20007|xxnet-to-gae-20009|xxnet-to-gae-20010|xxnet-to-gae-20011|xxnet-to-gae-20012