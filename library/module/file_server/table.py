from sqlalchemy import Column, Integer, DateTime, String, Boolean

from library.util.orm import Base


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
