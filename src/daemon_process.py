import shlex
import threading
import time

import daemon

from config import Config
from github_client import GitHubClient
from notifier import Notifier
from llm import LLM
from report_generator import ReportGenerator
from scheduler import Scheduler
from logger import LOG
from subscription_manager import SubscriptionManager

# 定时器启动文件
def run_scheduler(scheduler):
    # 启动调度器的函数，用于在线程中运行
    scheduler.start()

def main():
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    llm = LLM()
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)

    scheduler = Scheduler(
        github_client=github_client,
        notifier=notifier,
        report_generator=report_generator,
        subscription_manager=subscription_manager,
        interval=config.update_interval
    )

    scheduler_thread = threading.Thread(target=run_scheduler, args=(scheduler,))
    scheduler_thread.daemon = True
    scheduler_thread.start()

    LOG.info("Scheduler thread started.")

    # 使用 python-daemon 库，以守护进程方式运行呈现
    with daemon.DaemonContext:
        try:
            while True:
                time.sleep(config.update_interval) # 按配置的更新间隔休眠
        except KeyboardInterrupt:
            LOG.info('Daemon process stopped.') # 在接收到中断信号时记录日志


if __name__ == '__main__':
    main()

# 启动方式：nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &