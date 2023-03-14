from creart import add_creator

from library.service.creator import (
    BotListCreator,
    ColorCreator,
    EricCoreCreator,
    FastAPICreator,
    GroupConfigCreator,
    LockSmithCreator,
    PermissionRegistryCreator,
    SessionContainerCreator,
    UserRegistryCreator,
)
from library.service.launchable import (
    EricCoreBotList,
    EricCoreData,
    EricCoreMisc,
    EricCoreUpdater,
    EricUtilSession,
    FrequencyLimitService,
)

__all__ = [
    "EricCoreBotList",
    "EricCoreData",
    "EricCoreMisc",
    "EricCoreUpdater",
    "FrequencyLimitService",
    "EricUtilSession",
]

add_creator(BotListCreator)
add_creator(ColorCreator)
add_creator(EricCoreCreator)
add_creator(FastAPICreator)
add_creator(GroupConfigCreator)
add_creator(LockSmithCreator)
add_creator(PermissionRegistryCreator)
add_creator(SessionContainerCreator)
add_creator(UserRegistryCreator)
