# src/llm.py

import os
from openai import OpenAI

from logger import LOG


class LLM:
    def __init__(self):
        api_key=os.getenv('YI_API_KEY')
        self.client = OpenAI(
            base_url="https://vip.apiyi.com/v1",
            api_key=api_key
        )
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")


    def generate_daily_report(self, markdown_content, dry_run=False):
        prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}"
        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")

            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)

            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("Starting report generation using GPT model.")
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role':'system','content':'你是一个报告专家，确保始终使用中文生成报告，对每份报告进行分析总结'},
                    {"role": "user", "content": prompt}
                ]
            )
            LOG.debug("GPT response:{}",response)
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise