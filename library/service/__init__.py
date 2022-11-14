from creart import add_creator

from library.service.creator.core_creator import EricCoreCreator
from library.service.creator.fastapi_creator import FastAPICreator
from library.service.creator.group_config import GroupConfigCreator

add_creator(EricCoreCreator)
add_creator(FastAPICreator)
add_creator(GroupConfigCreator)
