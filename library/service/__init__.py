from creart import add_creator

from library.service.creator.core_creator import EricCoreCreator
from library.service.creator.fastapi_creator import FastAPICreator

add_creator(EricCoreCreator)
add_creator(FastAPICreator)
