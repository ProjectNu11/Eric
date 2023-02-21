from creart import add_creator

from library.service.creator import (
    BotListCreator,
    EricCoreCreator,
    FastAPICreator,
    GroupConfigCreator,
    LockSmithCreator,
    PermissionRegistryCreator,
    SessionContainerCreator,
    UserRegistryCreator,
)

add_creator(BotListCreator)
add_creator(EricCoreCreator)
add_creator(FastAPICreator)
add_creator(GroupConfigCreator)
add_creator(LockSmithCreator)
add_creator(PermissionRegistryCreator)
add_creator(SessionContainerCreator)
add_creator(UserRegistryCreator)
