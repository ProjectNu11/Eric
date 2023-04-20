from abc import abstractmethod

from loguru import logger


class BaseMigrator:
    """所有迁移器的基类"""

    @property
    @abstractmethod
    def dest_version(self) -> str:
        """目标版本"""
        pass

    @abstractmethod
    def run(self):
        """运行迁移器"""
        pass

    def log_and_run(self):
        """运行迁移器并记录日志"""
        try:
            logger.info(f"[Migrator] 正在运行迁移器 {self.dest_version}")
            self.run()
        except Exception as e:
            logger.error(f"[Migrator] 迁移器 {self.dest_version} 运行失败")
            logger.exception(e)
            raise e
        else:
            logger.info(f"[Migrator] 迁移器 {self.dest_version} 运行完毕")
