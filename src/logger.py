# 日志模块
import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout,level='DEBUG',format='{time} {level} {message}',colorize=True)
logger.add('logs/app.log',rotation='1 MB',level='DEBUG')

# Alias the logger for easier import
LOG = logger

# Make the logger available for import with the alias
__all__ = ['LOG']