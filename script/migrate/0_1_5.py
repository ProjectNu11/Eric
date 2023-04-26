from pathlib import Path

from loguru import logger

from script.migrate.base import BaseMigrator


class Migrator(BaseMigrator):
    @property
    def dest_version(self) -> str:
        return "0.1.5"

    @staticmethod
    def run_cleanup():
        if (old_lock := Path(".lock-hash")).is_file():
            old_lock.unlink()
            logger.info("[Migrator] 已删除旧的锁文件")

    def run(self):
        self.run_cleanup()
