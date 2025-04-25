import json
import os


class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.github_token = os.getenv('GITHUB_TOKEN')

            # 初始化电子邮件配置
            self.email = config.get('email',{})
            self.email['password'] = os.getenv('163_SMTP_PASS', self.email.get('password', ''))

            self.subscriptions_file = config.get('subscriptions_file')

            # 默认每天执行
            self.freq_days = config.get('github_progress_frequency_days',1)
            # 默认早上8点更新（操作系统默认时区时 UTC +0，08点刚好对于北京时间凌晨12点）
            self.exec_time = config.get('github_progress_execution_time', "08:00")
