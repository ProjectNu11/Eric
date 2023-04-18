from sqlalchemy import BIGINT, TEXT, Column, DateTime, Integer, String

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


class UserProfileTable(Base):
    """用户资料"""

    __tablename__ = "user_profile"

    id = Column(BIGINT, nullable=False, primary_key=True)
    """ 用户ID """

    fields = Column(TEXT, nullable=False)
    """ 用户组ID列表 """

    name = Column(TEXT, nullable=False)
    """ 用户名 """

    nickname = Column(TEXT, nullable=False)
    """ 昵称 """

    preferred_name = Column(TEXT, nullable=False)
    """ 首选名 """

    chat_count = Column(BIGINT, nullable=False)
    """ 聊天次数 """

    usage_count = Column(BIGINT, nullable=False)
    """ 使用次数 """

    permission = Column(TEXT, nullable=False)
    """ 权限 """

    fg_permission = Column(TEXT, nullable=False)
    """ 细粒度权限 """

    module_preferences = Column(TEXT, nullable=False)
    """ 模块偏好设置 """
