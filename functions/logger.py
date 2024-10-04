import logging
import os

class DataLogger:
    def __init__(self, log_file='data_log.log'):
        """初始化日志类"""
        self.logger = logging.getLogger('DataLogger')
        self.logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

        # 创建一个处理器，用于写入日志文件
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # 处理器的日志级别

        # 创建一个格式化器，并将其添加到处理器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        self.logger.addHandler(file_handler)

    def log_info(self, message):
        """记录信息级别的日志"""
        self.logger.info(message)

    def log_warning(self, message):
        """记录警告级别的日志"""
        self.logger.warning(message)

    def log_error(self, message):
        """记录错误级别的日志"""
        self.logger.error(message)

    def log_debug(self, message):
        """记录调试级别的日志"""
        self.logger.debug(message)

    def close(self):
        """关闭日志处理器"""
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)


# 使用示例
if __name__ == '__main__':
    logger = DataLogger('my_data_log.log')

    logger.log_info('This is an informational message.')
    logger.log_warning('This is a warning message.')
    logger.log_error('This is an error message.')
    logger.log_debug('This is a debug message.')

    logger.close()  # 关闭日志处理器
