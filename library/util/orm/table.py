from sqlalchemy import (
    BIGINT,
    TEXT,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

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

    name = Column(TEXT, nullable=False)
    """ 用户名 """

    permission = Column(TEXT, nullable=False)
    """ 权限，只能为 `UserPerm` 中已定义的值 """

    fg_permission = Column(TEXT, nullable=False)
    """ 细粒度权限，格式为 `permission1,permission2,permission3` """


class FileServer(Base):
    """文件服务器"""

    __tablename__ = "file_server"

    id = Column(Integer, primary_key=True)
    """ 记录ID """

    time = Column(DateTime, nullable=False)
    """ 写入时间 """

    uuid = Column(String(length=4000), nullable=False)
    """ 文件 ID """

    filename = Column(String(length=4000), nullable=False)
    """ 文件名 """

    lifespan = Column(Integer, nullable=False)
    """ 生命周期 """

    available = Column(Boolean, default=True, nullable=False)
    """ 是否可用 """

    hash = Column(String(length=4000), nullable=False)
    """ 文件哈希（前 10MB） """


class MessageRecord(Base):
    """消息记录表"""

    __tablename__ = "message_record"

    time = Column(DateTime, nullable=False)
    """ 消息时间 """

    msg_id = Column(BigInteger, nullable=False, primary_key=True)
    """ 消息 ID """

    target = Column(BigInteger, nullable=False, primary_key=True)
    """ 目标 ID，正数为群号，负数为私聊 ID """

    target_name = Column(Text, nullable=False)
    """ 目标名称 """

    sender = Column(BigInteger, nullable=False)
    """ 发送者 ID """

    sender_name = Column(Text, nullable=False)
    """ 发送者名称 """

    content = Column(Text, nullable=False)
    """ 消息内容 """

    message_chain = Column(Text, nullable=False)
    """ 消息链 """
