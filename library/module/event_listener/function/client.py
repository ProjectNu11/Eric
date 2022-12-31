from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import OtherClientOfflineEvent, OtherClientOnlineEvent
from loguru import logger

from library.module.event_listener.util import _get_cfg
from library.util.message import broadcast_to_owners


# other_client_offline_event
async def other_client_offline_event(app: Ariadne, event: OtherClientOfflineEvent):
    client = event.client
    platform = client.platform
    logger.info(f"[EventListener] 其他客户端 {client.id} ({platform}) 离线")
    msg, owner_msg = _get_cfg(0, event, client=client, id=client.id, platform=platform)
    await broadcast_to_owners(owner_msg, app.account)


# other_client_online_event
async def other_client_online_event(app: Ariadne, event: OtherClientOnlineEvent):
    client = event.client
    platform = client.platform
    logger.info(f"[EventListener] 其他客户端 {client.id} ({platform}) 上线")
    msg, owner_msg = _get_cfg(0, event, client=client, id=client.id, platform=platform)
    await broadcast_to_owners(owner_msg, app.account)
