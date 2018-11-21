def test_print1():
    from datetime import datetime
    print("===111====" + str(datetime.now()) + "========")

def test_print2():
    from datetime import datetime
    print("===222====" + str(datetime.now()) + "========")

def test_print3():
    from datetime import datetime
    print("===333====" + str(datetime.now()) + "========")

CronParams = {
    "func": None,
    "trigger": 'cron',
    "hour": "*",
    "day": "*",
    "month": "*",
    "minute": "*",
    "week": "*",
    "second": "0",
}

def get_test_cron_tragger_str():
    res_cron_tasks = []
    funcs = [test_print1, test_print2, test_print3]
    i = 1
    for func in funcs:
        temp_params = CronParams.copy()
        temp_params["second"] = "*/{second}".format(second=i+1)
        temp_params["func"] = func
        res_cron_tasks.append(temp_params)
        i += 1
    return res_cron_tasks


def schedule_task():
    from apscheduler.schedulers.blocking import BlockingScheduler

    res_cron_tasks = get_test_cron_tragger_str()
    print("===============================================")
    print(res_cron_tasks)
    print("===============================================")
    scheduler = BlockingScheduler()
    for res_cron in res_cron_tasks:

        scheduler.add_job(**res_cron)
        #    scheduler.add_job(func=alert_gen_polling, args=(config_dict,), trigger='interval', seconds=5)
        #    scheduler.add_job(func=update_ip_statistics, args=(config_dict,), trigger='interval', seconds=5)
    print(scheduler.print_jobs())
    scheduler.start()


def task():
    from apscheduler.schedulers.blocking import BlockingScheduler

    res_cron_tasks = get_test_cron_tragger_str()
    scheduler = BlockingScheduler()
    for res_cron in res_cron_tasks:
        scheduler.add_job(**res_cron)
        #    scheduler.add_job(func=alert_gen_polling, args=(config_dict,), trigger='interval', seconds=5)
        #    scheduler.add_job(func=update_ip_statistics, args=(config_dict,), trigger='interval', seconds=5)
    print(scheduler.print_jobs())
    scheduler.start()
