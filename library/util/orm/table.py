from sqlalchemy import BIGINT, Column, DateTime, Integer, String

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
