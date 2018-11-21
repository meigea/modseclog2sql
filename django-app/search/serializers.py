# coding:utf-8
from rest_framework import serializers

## 放弃使用
class AccesslogSearchSerializer(serializers.Serializer):
    request_method = serializers.CharField(label=u'HTTP方法(,)', required=False, allow_blank=True, max_length=100)
    request_version = serializers.CharField(label=u'HTTP版本(,)', required=False, allow_blank=True, max_length=100)
    remote_addr = serializers.CharField(label=u'源IP(,)', required=False, allow_blank=True, max_length=100)
    remote_user = serializers.CharField(label=u'源用户', required=False, allow_blank=True, max_length=100)
    request_url = serializers.CharField(label=u'URL搜索RE', required=False, allow_blank=True, max_length=100)
    device = serializers.CharField(label=u'设备', required=False, allow_blank=True, max_length=100)
    os = serializers.CharField(label=u'操作系统', required=False, allow_blank=True, max_length=100)
    user_agent = serializers.CharField(label=u'客户端', required=False, allow_blank=True, max_length=100)

    status = serializers.IntegerField(label=u'请求状态码',)
    body_bytes_sent = serializers.IntegerField(label=u'发送的大小',)

    is_limit10 = serializers.BooleanField(label=u'限定前10', required=False)
    is_ignore_static = serializers.BooleanField(label=u'无视静态文件', required=False)
    limit_static = serializers.BooleanField(label=u'只要静态文件', required=False)


    def update(self, validated_data):
        instance = dict(
            request_method = validated_data.get('request_method', None),
            request_version = validated_data.get('request_version', None),
            remote_addr = validated_data.get('remote_addr', None),
            remote_user = validated_data.get('language', None),
            request_url = validated_data.get('request_url', None),
            device = validated_data.get('device', None),
            os = validated_data.get('os', None),
            user_agent = validated_data.get('user_agent', None),
            status = validated_data.get('status', None),
            body_bytes_sent = validated_data.get('status', None),
            is_limit10 = validated_data.get('is_limit10', None),
            is_ignore_static = validated_data.get('is_ignore_static', None),
            limit_static = validated_data.get('limit_static', None),
        )

        from wafmanage.utils.db_utils import from_sql_get_data
        from .prescan import get_static_suffix2
        res_data = from_sql_get_data(get_static_suffix2(**instance))["data"]
        return res_data