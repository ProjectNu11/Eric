from creart import it
from graia.saya import Channel
from graiax.shortcut import listen
from loguru import logger

from library.model.event.util import UserProfilePendingUpdate
from library.util.locksmith import LockSmith

channel = Channel.current()


@listen(UserProfilePendingUpdate)
async def update_user_profile(event: UserProfilePendingUpdate):
    update_lock = it(LockSmith).get(f"{channel.module}:user_profile")
    async with update_lock:
        logger.info(f"[Manager] Updating profile for {event.profile.id}...")
        _ = event.profile
        # TODO Implement this
