from sqlalchemy import BIGINT, Column, DateTime, Integer, String, Float

from library.util.orm import Base


class FunctionCallRecord(Base):
    """功能调用记录"""

    __tablename__ = "function_call_record"

    id = Column(Integer, primary_key=True)
    """ 记录ID """

    time = Column(DateTime, nullable=False)
    """ 调用时间 """

    field = Column(BIGINT, nullable=False)
    """ 聊天区域"""

    supplicant = Column(BIGINT, nullable=False)
    """ 调用者 """

    function = Column(String(length=4000), nullable=False)
    """ 调用功能 """


class BlacklistTable(Base):
    """黑名单"""

    __tablename__ = "blacklist"

    field = Column(BIGINT, nullable=False, primary_key=True)
    """ 聊天区域 """

    target = Column(BIGINT, nullable=False, primary_key=True)
    """ 黑名单对象 """

    time = Column(DateTime, nullable=False)
    """ 加入时间 """

    reason = Column(String(length=4000), nullable=False)
    """ 加入原因 """

    supplicant = Column(BIGINT, nullable=False)
    """ 操作者 """


class TempBlacklistTable(Base):
    """临时黑名单"""

    __tablename__ = "temp_blacklist"

    field = Column(BIGINT, nullable=False, primary_key=True)
    """ 聊天区域 """

    target = Column(BIGINT, nullable=False, primary_key=True)
    """ 黑名单对象 """

    time = Column(DateTime, nullable=False)
    """ 加入时间 """

    reason = Column(String(length=4000), nullable=False)
    """ 加入原因 """

    supplicant = Column(BIGINT, nullable=False)
    """ 操作者 """

    duration = Column(Integer, nullable=False)
    """ 持续时间（秒） """


class ProcessTimeStat(Base):
    """处理时间统计"""

    __tablename__ = "process_time_stat"

    id = Column(Integer, primary_key=True)
    """ 记录ID """

    time = Column(DateTime, nullable=False)
    """ 调用时间 """

    module = Column(String(length=4000), nullable=False)
    """ 模块名 """

    function = Column(String(length=4000), nullable=False)
    """ 调用功能 """

    time_used = Column(Float, nullable=False)
    """ 耗时 """
