from requests import Session, request
from time import time
from json import dumps
from datetime import datetime
from environs import Env
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger

session = Session()

env = Env()
env.read_env()

BASE_URL = "https://actionview.knowyourself.cc/actionview/api"
PUHS_URL = "https://push.dongxin.cool/v1/message/send"

LOGIN_URL = BASE_URL + "/session"
TASK_URL = BASE_URL + "/project/p_kyapp/issue"

TYPE = {"BUG": "8", "TASK": "6"}

headers = {"Content-Type": "application/json"}

log_id = logger.add('run.log', rotation="1 week", encoding="utf-8", retention="7 days", backtrace=True, catch=True)

def pushMsg(msg):
    data = {
        "token": env("PUSH_TOKEN"),
        "title": "ActionView提醒",
        "content": f"ActionView提醒，BUG: {msg['b']}，任务: {msg['t']}，其他: {msg['o']}",
        "tempalte": "text"
    }
    res = request("POST", PUHS_URL, headers=headers, data=dumps(data))
    if res.status_code == 200:
        logger.info('已发送通知')
    else:
        logger.info('通知异常')

def task():
    logger.info('{}遍历bug池', datetime.now())
    data = {"email": env("EMAIL"), "password": env("PASSWORD")}

    session = Session()
    session.post(LOGIN_URL, headers=headers, data=dumps(data))

    result = {
        "b": 0,
        "t": 0,
        "o": 0,
    }

    params = f"?assignee=me&resolution=Unresolved&state=Open&page=1&requested_at=${int(time()) * 1000}"

    url = TASK_URL + params

    data = session.get(url).json()["data"]
    for item in data:
        if item["type"] == TYPE["BUG"]:
            result["b"] += 1
            continue
        elif item["type"] == TYPE["TASK"]:
            result["t"] += 1
            continue
        else:
            result["o"] += 1
            continue

    pushMsg(result)

def weekReport():
    print(f"{datetime.now()}遍历周报")
    data = {"email": env("EMAIL"), "password": env("PASSWORD")}

    session = Session()
    session.post(LOGIN_URL, headers=headers, data=dumps(data))

if __name__ == "__main__":
    task()
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(task, "cron", day_of_week="mon-fri", hour="8,13,17", minute=40, max_instances=10)
    scheduler.start()