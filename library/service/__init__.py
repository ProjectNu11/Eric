from creart import add_creator

from library.service.creator import (
    BotListCreator,
    EricCoreCreator,
    FastAPICreator,
    GroupConfigCreator,
    LockSmithCreator,
    SessionContainerCreator,
)

add_creator(EricCoreCreator)
add_creator(FastAPICreator)
add_creator(GroupConfigCreator)
add_creator(BotListCreator)
add_creator(SessionContainerCreator)
add_creator(LockSmithCreator)
