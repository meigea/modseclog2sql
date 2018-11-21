# coding:utf-8
from django.db import models

class NginxAccessLogDetail(models.Model):
    # id=models.UUIDField(primary_key=True, default=uuid4)
    request_id = models.CharField(u"请求ID", max_length=255, unique=True)
    remote_addr = models.CharField(u"请求IP", max_length=55, default="0.0.0.0")
    remote_user = models.CharField(u"用户", max_length=255, default="")
    time_local = models.DateTimeField(u"时间")
    request = models.TextField(u"请求", default="")
    status = models.IntegerField(u"请求状态", default="110")
    body_bytes_sent = models.IntegerField(u"请求体字节", default=0)
    http_user_agent = models.TextField(u"客户端[详细]", default="")
    http_referer = models.TextField(u"指向的位置", max_length=255, default="")
    user_agent = models.CharField(u"客户端", max_length=255, default="")
    os = models.CharField(u"操作系统", max_length=255, default="")
    device = models.CharField(u"设备", max_length=255, default="")
    http_x_forwarded_for = models.CharField(u"获取IP地址", max_length=255, default="")

    server_port = models.IntegerField(u"服务端口", default=80)

    class Meta:
        verbose_name = u"Nginx访问日志"
        db_table = "accesslog"


class ModSecLogPhaserHinfo(models.Model):
    # userId = ForeignKey(user)
    # roleId = ForeignKey(role)
    rule_id = models.IntegerField(u"规则ID")
    msg = models.CharField(u"告警消息", max_length=255, default="")
    matched_data = models.TextField(u"抓到的包", default="")

    def __str__(self):
        return "【" + str(self.rule_id) + "】(" + self.msg + ")"

    class Meta:
        # unique_together = ("rule_id", "msg", "matched_data")
        verbose_name = u"waf告警内容H阶段详情分条目"
        db_table = "modsechinfo"


class ModsecLogDetail(models.Model):
    audit_logid = models.CharField(u"告警日志标号", max_length=155, default="")
    logsize = models.IntegerField(u"日志大小", default=0)
    http_user_agent = models.TextField(u"客户端", default="")
    http_ver = models.CharField(u"Http版本", max_length=155, default="")
    src_host = models.CharField(u"源Host", max_length=155, default="")
    src_ip = models.CharField(u"源IP", max_length=155, default="")
    waf_serv = models.CharField(u"waf服务端版本", max_length=155, default="")
    audit_time = models.DateTimeField(u"审计日志时间")
    content_length = models.IntegerField(u"内容长度", default=0)
    resp_code = models.IntegerField(u"详情状态码", default=0)
    uniq_id = models.CharField(u"告警条目的ID", max_length=255, default="")
    request_url = models.CharField(u"请求的URL", max_length=255, default="")
    request_method = models.CharField(u"请求方法", max_length=16, default="")
    content_type = models.CharField(u"请求内容类型", max_length=155, default="")
    hloginfo = models.ManyToManyField(ModSecLogPhaserHinfo, verbose_name=u"H阶段的信息")

    server_port = models.IntegerField(u"服务端口", default=80)

    class Meta:
        verbose_name = u"WAF告警日志内容"
        ordering = ["-audit_time"]
        db_table = "modseclog"

