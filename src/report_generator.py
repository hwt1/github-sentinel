# src/report_generator.py
import os
from datetime import date, timedelta, datetime
from pathlib import Path

from logger import LOG


class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm

    def export_daily_progress(self, repo, updates):
        # 构建仓库的日志文件目录
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)  # 如果目录不存在则创建

        # 创建并写入日常进展的Markdown文件
        file_path = os.path.join(repo_dir, f'{date.today()}.md')
        with open(file_path, 'w') as file:
            file.write(f"# Daily Progress for {repo} ({date.today()})\n\n")
            file.write("\n## Issues\n")
            for issue in updates['issues']:
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write("\n## Pull Requests\n")
            for pr in updates['pull_requests']:
                file.write(f"- {pr['title']} #{pr['number']}\n")
        return file_path

    def export_progress_by_date_range(self, repo, updates, days):
        # 构建目录并写入特定日期范围的进展Markdown文件
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)

        today = date.today()
        since = today - timedelta(days=days)  # 计算起始日期

        date_str = f"{since}_to_{today}"  # 格式化日期范围字符串
        file_path = os.path.join(repo_dir, f'{date_str}.md')

        with open(file_path, 'w') as file:
            file.write(f"# Progress for {repo} ({since} to {today})\n\n")
            file.write("\n## Issues Closed in the Last {days} Days\n")
            for issue in updates['issues']:
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write("\n## Pull Requests Merged in the Last {days} Days\n")
            for pr in updates['pull_requests']:
                file.write(f"- {pr['title']} #{pr['number']}\n")

        LOG.info(f"Exported time-range progress to {file_path}")  # 记录导出日志
        return file_path

    def generate_daily_report(self, markdown_file_path):
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+',encoding='UTF-8') as report_file:
            report_file.write(report)

        LOG.info(f"Generated report saved to {report_file_path}")

    def generate_report_by_date_range(self,markdown_file_path,days):
        # 生成特定日期范围的报告，流程与日报生成类似
        with open(markdown_file_path,'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)
        report_file_path = os.path.splitext(markdown_file_path)[0] + f"_report.md"
        with open(report_file_path, 'w+',encoding='utf-8') as report_file:
            report_file.write(report)

        LOG.info(f"Generated report saved to {report_file_path}")  # 记录生成报告日志
        return report,report_file_path

    def generate_hacker_news_report(self,top_stories):
        report = self.llm.generate_hacker_news_report(top_stories)

        repo_dir = Path('daily_progress/hacker_news')
        repo_dir.mkdir(parents=True,exist_ok=True)

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H")  # e.g., 2025-04-25_15

        report_file_path = str(repo_dir / f"hacker_news_{timestamp}.md")
        with open(report_file_path,'w+',encoding='utf-8') as report_file:
            report_file.write(report)

        LOG.info(f"Generated report saved to {report_file_path}")  # 记录生成报告日志
        return report,report_file_path