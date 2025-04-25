import gradio as gr

from config import Config
from github_client import GitHubClient
from llm import LLM
from report_generator import ReportGenerator
from hacker_news_client import HackerNewsClient
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

def export_hacker_news_progress():
    top_stories = HackerNewsClient.fetch_hackernews_top_stories()
    report,report_file_path = report_generator.generate_hacker_news_report(top_stories)
    return report,report_file_path

def add_subscription(item):
    subscription_manager.add_subscription(item)
    subs = subscription_manager.list_subscriptions()
    return [[s] for s in subs],'',gr.update(choices=subs)

def remove_subscription(selected):
    if selected:
        print(f"需要删除的仓库："+selected)
        subscription_manager.remove_subscription(selected)
    subs = subscription_manager.list_subscriptions()
    return [[s] for s in subs],gr.update(choices=subs)
def load_subscriptions():
    subs = subscription_manager.list_subscriptions()
    return [[s] for s in subs], gr.update(choices=subs)

# 创建 Gradio 界面
with gr.Blocks() as app:
    with gr.Tabs():
        with gr.Tab("📊 GitHub报告生成") as github_report_tab:
            gr.Markdown('## GitHub 项目进展报告生成器')

            dropdown = gr.Dropdown(
                choices=subscription_manager.list_subscriptions(),
                label='订阅列表',
                info='已订阅的GitHub项目'
            )
            slider = gr.Slider(value=2,minimum=1,maximum=7,step=1,label='报告周期',info='生成过去几天的进展')
            generate_btn= gr.Button('生成报告')
            report_md = gr.Markdown()
            report_file = gr.File(label='下载报告')

            generate_btn.click(export_progress_by_date_range, inputs=[dropdown, slider], outputs=[report_md, report_file])

            # 当前切换到该tab时，刷新下拉选项
            github_report_tab.select(lambda : gr.update(choices=subscription_manager.list_subscriptions()),outputs=dropdown)

        with gr.Tab('📋 订阅管理') as subscription_tab:
            gr.Markdown('### 📋 订阅仓库管理')

            table = gr.Dataframe(headers=['订阅仓库'], interactive=False)

            with gr.Row():
                new_item = gr.Textbox(label='新增')
                add_btn = gr.Button("➕ 添加")
            with gr.Row():
                dropdown = gr.Dropdown(label='选择要删除的任务')
                del_btn = gr.Button("🗑️ 删除所选行")

            # 每次进入 Tab 时刷新数据
            subscription_tab.select(load_subscriptions, outputs=[table, dropdown])

            add_btn.click(add_subscription, inputs=[new_item], outputs=[table, new_item, dropdown])
            del_btn.click(remove_subscription, inputs=[dropdown], outputs=[table, dropdown])

        with gr.Tab("📊 HackerNews报告生成") as hacker_report_tab:
            gr.Markdown('## HackerNews 项目进展报告生成器-实时')

            generate_btn= gr.Button('生成报告')
            report_md = gr.Markdown()
            report_file = gr.File(label='下载报告')

            generate_btn.click(export_hacker_news_progress, outputs=[report_md, report_file])



if __name__ == '__main__':
    app.launch(share=True,server_name='127.0.0.1') # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True,server_name = '127.0.0.1',auth = ('hwt','1234'))