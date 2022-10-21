from datetime import datetime
from pathlib import Path


class EricCore:
    __launch_time: datetime
    """ 启动时间 """

    __working_dir: Path
    """ 工作目录 """

    __initialized: bool = False
    """ 是否已初始化 """

    def __init__(self):
        self.__launch_time = datetime.now()
        self.__working_dir = Path.cwd()

    @property
    def launch_time(self) -> datetime:
        """获取启动时间"""
        return self.__launch_time

    @property
    def working_dir(self) -> Path:
        """获取工作目录"""
        return self.__working_dir

    @property
    def initialized(self) -> bool:
        """是否已初始化"""
        return self.__initialized

    def finish_init(self):
        """完成初始化"""
        self.__initialized = True
