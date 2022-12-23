from creart import add_creator

from library.service.creator.bot_list import BotListCreator
from library.service.creator.core_creator import EricCoreCreator
from library.service.creator.fastapi_creator import FastAPICreator
from library.service.creator.group_config import GroupConfigCreator
from library.service.creator.session_container import SessionContainerCreator

add_creator(EricCoreCreator)
add_creator(FastAPICreator)
add_creator(GroupConfigCreator)
add_creator(BotListCreator)
add_creator(SessionContainerCreator)
