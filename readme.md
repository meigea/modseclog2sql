# Nginx-modseurity 日志处理

## 日志处理的核心文件位置
> 主要参考这个即可, syslog是之前的淘汰版本 

- [文本处理](./fatal_v11/scripts/get_common_logs.py)

## 如果要用txt-to-Mysql
- 工具在`django-app`的模板中

## nginx-accesslog 格式

```
log_format  custom '$remote_addr - $remote_user [$time_local] '
'"$request" $status $body_bytes_sent '
'"$http_referer" "$http_user_agent" '
'"$http_x_forwarded_for" $request_id ';
```

## 需要的工具包
- PyMySQL==0.9.2
- pymongo==3.6.1
- ua-parser==0.8.0
