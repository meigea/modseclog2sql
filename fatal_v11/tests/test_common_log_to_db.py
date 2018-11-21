from fatal_v11.scripts.log_to_mysql import LogToSql
from fatal_v11.scripts.log_to_mongo import LogToMongo

def test_accesslog_2_mysql():
    filename = "A:\\1\\demo\\localhost-8080.access.log"
    LogToSql(filename=filename).accesslog_to_sql()


def test_modseclog_2_mysql():
    filename = "A:\\1\\demo\\modsec_audit.log"
    LogToSql(filename=filename).modseclog_to_sql()

from fatal_v11.scripts.log_to_mysql import LogToSql


def test_accesslog_2_mongo():
    filename = "A:\\1\\demo\\localhost-8080.access.log"
    LogToMongo(filename=filename).accesslog_to_mongo()


def test_modseclog_2_mongo():
    filename = "A:\\1\\demo\\modsec_audit.log"
    LogToMongo(filename=filename).modseclog_to_mongo()
