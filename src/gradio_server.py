import gradio as gr

from config import Config
from github_client import GitHubClient
from llm import LLM
from report_generator import ReportGenerator
from subscription_manager import SubscriptionManager

# gradio 页面方式启动

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo,days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo,days)
    report,report_file_path = report_generator.generate_report_by_date_range(raw_file_path,days)
    return report,report_file_path

# 创建 Gradio 界面
demo = gr.Interface(
    fn=export_progress_by_date_range,
    title='GitHubSentinel',
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(),label='订阅列表',info='已订阅GitHub项目'
        ),
        gr.Slider(value=2,minimum=1,maximum=7,step=1,label='报告周期',info='生成项目过去一段时间进展，单位：天')
    ],
    outputs=[gr.Markdown(),gr.File(label='下载报告')]
)

if __name__ == '__main__':
    demo.launch(share=False,server_name='127.0.0.1') # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True,server_name = '127.0.0.1',auth = ('hwt','1234'))