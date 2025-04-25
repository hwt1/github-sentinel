import sys
import signal
import time

import schedule

from config import Config
from github_client import GitHubClient
from llm import LLM
from logger import LOG
from notifier import Notifier
from report_generator import ReportGenerator
from subscription_manager import SubscriptionManager


def graceful_shutdown(signum,frame):
    # 优雅关闭程序的函数，处理信号时调用
    LOG.info("[优雅退出]守护进程接收到终止信号")
    sys.exit(0)

def github_job(subscription_manager,github_client,report_generator,notifier,days):
    LOG.info('[开始执行定时任务]')
    subscriptions = subscription_manager.list_subscriptions()
    LOG.info(f"订阅列表：{subscriptions}")

    for repo in subscriptions:
        # 遍历每个订阅仓库，执行以下操作
        markdown_file_path = github_client.export_progress_by_date_range(repo,days)

        report,report_file_path = report_generator.generate_report_by_date_range(markdown_file_path,days)
        notifier.notify(repo,report)
    LOG.info(f"[定时任务执行完毕]")

def main():
    # 设置信号处理器
    signal.signal(signal.SIGTERM,graceful_shutdown)

    config = Config()
    github_client = GitHubClient(config.github_token) # 创建GitHub客户端实例
    notifier = Notifier(config.email) # 创建通知器实例
    llm=LLM() # 创建语言模型实例
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)

    # 启动时立即执行（如不需要可注释）
    github_job(subscription_manager,github_client,report_generator,notifier,config.freq_days)

    # 安排每天的定时任务
    schedule.every(config.freq_days).days.at(
        config.exec_time
    ).do(github_job,subscription_manager,github_client,report_generator,notifier,config.freq_days)

    try:
        # 在守护进程中持续运行
        while True:
            schedule.run_pending()
            time.sleep(1) # 短暂休眠以减少 CPU 使用
    except Exception as e:
        LOG.error(f"主进程发生异常：{str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()