from pydantic import BaseModel


class ModuleMetadata(BaseModel):
    """模块元数据"""

    name: str
    """ 模块名称 """

    version: str
    """ 模块版本 """

    pack: str
    """ 模块包名 """

    authors: list[str]
    """ 模块作者 """

    description: str
    """ 模块描述 """

    icon: None | str = None
    """ 模块图标 """
