from sqlalchemy import BigInteger, Column, DateTime, Text

from library.util.orm import Base


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
