# src/github_client.py
import os
from datetime import timedelta

import requests
import datetime
from logger import LOG

class GitHubClient:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'token {self.token}'}

    def fetch_updates(self, repo,since=None,until=None):
        # 获取特定 repo 的更新（commits, issues, pull requests）
        # 可以指定开始和结束日期
        updates = {
            'commits': self.fetch_commits(repo,since,until),
            'issues': self.fetch_issues(repo,since,until),
            'pull_requests': self.fetch_pull_requests(repo,since,until)
        }
        return updates

    def fetch_commits(self, repo,since=None,until=None):
        url = f'https://api.github.com/repos/{repo}/commits'
        params = {}
        if since:
            params['since'] = since
        if until:
            params['until'] = until

        response = requests.get(url, headers=self.headers,params=params)
        response.raise_for_status() # 检查请求是否成功
        return response.json() # 返回 JSON格式的数据

    def fetch_issues(self, repo,since=None,until=None):
        url = f'https://api.github.com/repos/{repo}/issues'
        params = {
            'state':'closed', # 仅获取已关闭的问题
            'since':since,
            'until':until
        }
        response = requests.get(url, headers=self.headers,params=params)
        response.raise_for_status()
        return response.json()

    def fetch_pull_requests(self, repo,since=None,until=None):
        url = f'https://api.github.com/repos/{repo}/pulls'
        params={
            'state':'closed',
            'since':since,
            'until':until
        }
        response = requests.get(url, headers=self.headers,params=params)
        response.raise_for_status()
        return response.json()


    def export_daily_progress(self, repo):
        today = datetime.date.today().isoformat()

        updates = self.fetch_updates(repo,since=today)

        # 构建存储路径
        repo_dir = os.path.join('daily_progress',repo.replace("/","_"))
        os.makedirs(repo_dir,exist_ok=True) # 确保目录存在

        # 构建文件目录
        file_path = os.path.join(repo_dir,f'{today}.md')

        with open(file_path,'w') as file:
            file.write(f"# Daily Progress for {repo} ({today})\n\n")
            file.write('\n## Issues Closed Today \n')
            for issue in updates['issues']:
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write('\n## Pull Requests Merged Today\n')
            for pr in updates['pull_requests']:
                file.write(f"- {pr['title']} #{pr['number']}\n")
        LOG.info(f"Exported daily progress to {file_path}")
        return file_path

    def export_progress_by_date_range(self,repo,days):
        today= datetime.date.today()
        since = today - timedelta(days=days)

        updates = self.fetch_updates(repo,since=since.isoformat(),until=today.isoformat())
        repo_dir = os.path.join('daily_progress',repo.replace("/","_"))
        os.makedirs(repo_dir,exist_ok=True)

        # 更新文件名以包含日期范围
        date_str=f"{since}_to_{today}"
        file_path = os.path.join(repo_dir,f'{date_str}.md')

        with open(file_path,'w') as file:
            file.write(f"# Progress for {repo} ({since} to {today})\n\n")
            file.write(f"\n## Issues Closed in the Last {days} Days\n")
            for issue in updates['issues']:  # 写入在指定日期内关闭的问题
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write(f"\n## Pull Requests Merged in the Last {days} Days\n")
            for pr in updates['pull_requests']:  # 写入在指定日期内合并的拉取请求
                file.write(f"- {pr['title']} #{pr['number']}\n")

        LOG.info(f"Exported time-range progress to {file_path}")  # 记录日志
        return file_path