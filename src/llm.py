# src/llm.py

import os
from datetime import datetime

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

    # 将 hacker_news_client 生成的结果交给 OpenAI进行总结
    def generate_hacker_news_report(self,top_stories,dry_run=False):
        prompt=f"\n\n{top_stories}"
        if dry_run:
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open('daily_progress/hacker_news_prompt.txt','w+') as f:
                f.write(prompt)
            LOG.info('Prompt save to daily_progress/hacker_news_prompt.txt')
            return "DRY RUN"

        LOG.info("Starting hacker news report generation using GPT model.")
        try:
            with open('prompts/hacker_news_prompt.txt','r',encoding='utf-8') as f:
                system_prompt = f.read()

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H")  # e.g., 2025-04-25_15
            system_prompt = system_prompt.format(today=timestamp)
            # 请求LLM
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role':'system','content':system_prompt},
                    {'role':'user','content':prompt}
                ]
            )
            LOG.debug("GPT hacker news response:{}",response)
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the hacker news report: {}", e)
            raise


    # 将 github_client 返回的结果交给 OpenAI进行总结
    def generate_daily_report(self, markdown_content, dry_run=False):
        prompt = f"\n\n{markdown_content}"
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
            # 获取github项目的系统提示词
            with open('prompts/report_prompt.txt', 'r', encoding='utf-8') as f:
                system_prompts = f.read()
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role':'system','content':system_prompts},
                    {"role": "user", "content": prompt}
                ]
            )
            LOG.debug("GPT response:{}",response)
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise


if __name__ =='__main__':
    # from hacker_news_client import fetch_hackernews_top_stories
    # stories = fetch_hackernews_top_stories()
    # llm=LLM()
    # result = llm.generate_hacker_news_report(stories)
    # print(result)
    with open('prompts/hacker_news_prompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H")  # e.g., 2025-04-25_15
    system_prompt = system_prompt.format(today=timestamp)
    print(system_prompt)