import shlex

from config import Config
from github_client import GitHubClient
from notifier import Notifier
from llm import LLM
from report_generator import ReportGenerator
from command_handler import CommandHandler
from subscription_manager import SubscriptionManager


# 命令行启动方式
def main():
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    llm = LLM()
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)
    command_handler = CommandHandler(github_client, subscription_manager, report_generator)


    parser = command_handler.parser
    command_handler.print_help()

    while True:
        try:
            user_input = input("GitHub Sentinel> ")
            if user_input in ['exit', 'quit']:
                break
            try:
                args = parser.parse_args(shlex.split(user_input))
                if args.command is None:
                    continue
                args.func(args)
            except SystemExit as e:
                print("Invalid command. Type 'help' to see the list of available commands.")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()