import requests
import time
import json
from datetime import datetime
from environs import Env
from apscheduler.schedulers.blocking import BlockingScheduler

session = requests.Session()

env = Env()
env.read_env()

BASE_URL = "https://actionview.knowyourself.cc/actionview/api"
PUHS_URL = "https://push.dongxin.cool/v1/message/send"

LOGIN_URL = BASE_URL + "/session"
TASK_URL = BASE_URL + "/project/p_kyapp/issue"

TYPE = {"BUG": "8", "TASK": "6"}

headers = {"Content-Type": "application/json"}

def pushMsg(msg):
    data = {
        "token": env("PUSH_TOKEN"),
        "title": "ActionView提醒",
        "content": f"ActionView提醒，BUG: {msg['b']}，任务: {msg['t']}，其他: {msg['o']}",
        "tempalte": "text"
    }
    res = requests.request("POST", PUHS_URL, headers=headers, data=json.dumps(data))
    print(res.text)

def task():
    print(f"{datetime.now()}遍历bug池")
    data = {"email": env("EMAIL"), "password": env("PASSWORD")}

    session = requests.Session()
    session.post(LOGIN_URL, headers=headers, data=json.dumps(data))

    result = {
        "b": 0,
        "t": 0,
        "o": 0,
    }

    params = f"?assignee=me&resolution=Unresolved&state=Open&page=1&requested_at=${int(time.time()) * 1000}"

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

    session = requests.Session()
    session.post(LOGIN_URL, headers=headers, data=json.dumps(data))

if __name__ == "__main__":
    task()
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(task, "cron", day_of_week="mon-fri", hour="8,13,17", minute=40, max_instances=10)
    scheduler.start()