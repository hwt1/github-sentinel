import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown2

from logger import LOG
from report_type import Report_Type


class Notifier:
    def __init__(self, email_settings):
        self.email_settings = email_settings
    
    def notify(self,subject, report,report_type):
        # Implement notification logic, e.g., send email or Slack message
        if self.email_settings:
            self.send_email(subject,report,report_type)
        else:
            LOG.warning("邮件设置未配置正确，无法发送通知")

    def send_email(self,subject,report,report_type):
        LOG.info('准备发送邮件')
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']

        if report_type == Report_Type.GITHUB:
            msg['To'] =self.email_settings['github_to']
        elif report_type == Report_Type.HACKER:
            msg['To'] = self.email_settings['hacker_to']
        else:
            LOG.error('report type is not exist')

        msg['Subject'] = subject

        # 将Markdown内容转换为 HTML
        html_report = markdown2.markdown(report)
        LOG.info(html_report)

        msg.attach(MIMEText(html_report,'html'))
        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'],self.email_settings['smtp_port']) as server:
                LOG.debug('登录SMTP服务器')
                server.login(msg['From'],self.email_settings['password'])
                LOG.info(f"目标邮件地址：{msg['To']}")
                server.sendmail(msg['From'],msg['To'].split(','),msg.as_string())
                LOG.info('邮件发送成功')
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")


# 临时单元测试
if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email)
    test_repo = "DjangoPeng/openai-quickstart"
    test_report = """
# DjangoPeng/openai-quickstart 项目进展

## 时间周期：2024-08-24

## 新增功能
- Assistants API 代码与文档

## 主要改进
- 适配 LangChain 新版本

## 修复问题
- 关闭了一些未解决的问题。

"""
    notifier.notify(test_repo, test_report,Report_Type.HACKER)