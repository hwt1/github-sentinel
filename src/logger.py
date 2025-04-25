# 日志模块
import sys

from loguru import logger

# 定义统一的日志格式字符串
log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"

# 配置Loguru，移除默认的日志配置
logger.remove()

# 使用统一的日志格式配置标准输出和标准错误输出，支持彩色显示
logger.add(sys.stdout,level='DEBUG',format=log_format,colorize=True)
logger.add(sys.stderr,level='ERROR',format=log_format,colorize=True)

# 同样使用统一的格式配置日志文件输出，设置文件大小为 1MB自动轮换
logger.add('logs/app.log',rotation='1 MB',level='DEBUG',format=log_format)

# 为logger设置别名，方便在其他模块中导入和使用
LOG = logger


# 将 LOG变量公开，运行其他模块通过 from logger import LOG 来使用它
__all__ = ['LOG']