from graia.saya import Channel
from kayaku import config, create

from library.util.group_config import module_config, module_create
from library.util.group_config.util import module_save

channel = Channel.current()


@config(channel.module)
class _EventListenerConfig:
    """事件监听器配置"""

    bot_group_permission_change_event: str = (
        "Bot {app.account} 在群组 {group} 的权限由 {origin} 变更为 {current}"
    )
    """ 群权限变更事件 """
    bot_group_permission_change_event_switch: bool = True
    """ 群权限变更事件开关 """

    bot_join_group_event: str = "Bot {app.account} 加入群组 {group.name} ({group.id})"
    """ Bot 加入群事件 """
    bot_join_group_event_switch: bool = True
    """ Bot 加入群事件开关 """

    bot_unmute_event: str = (
        "Bot {app.account} 在群组 {group.name} ({int(group)}) "
        "被 {operator.name} ({operator}) 解除禁言"
    )
    """ Bot 被取消禁言事件 """
    bot_unmute_event_switch: bool = True
    """ Bot 被取消禁言事件开关 """

    bot_invited_join_group_request_event: str = (
        "收到邀请入群申请\n"
        "\n事件 ID: {uuid}"
        "\n邀请人: {supplicant}"
        "\n邀请人昵称: {nickname}"
        "\n邀请人留言: {message}"
        "\n邀请群: {source_group}"
        "\n邀请群名称: {group_name}\n"
        "\n发送 #通过 {uuid} 以接受入群申请"
        "\n发送 #拒绝 {uuid} 以拒绝入群申请"
    )
    """ Bot 被邀请入群申请事件 """
    bot_invited_join_group_request_event_switch: bool = True
    """ Bot 被邀请入群申请事件开关 """

    bot_leave_event_active: str = "Bot {app.account} 离开群组 {group.name} ({group.id})"
    """ Bot 主动离开群事件 """
    bot_leave_event_active_switch: bool = True
    """ Bot 主动离开群事件开关 """

    bot_leave_event_disband: str = (
        "Bot {app.account} 所在群组 {group.name} ({group.id}) 被解散"
    )
    """ Bot 被解散群事件 """
    bot_leave_event_disband_switch: bool = True
    """ Bot 被解散群事件开关 """

    bot_leave_event_kick: str = "Bot {app.account} 被踢出群组 {group.name} ({group.id})"
    """ Bot 被踢出群事件 """
    bot_leave_event_kick_switch: bool = True
    """ Bot 被踢出群事件开关 """

    bot_mute_event: str = (
        "Bot {app.account} 在群组 {group.name} ({group.id}) "
        "被 {operator.name} ({operator}) 禁言 {duration_repr}"
    )
    """ Bot 被禁言事件 """
    bot_mute_event_switch: bool = True
    """ Bot 被禁言事件开关 """

    bot_offline_event_active: str = ""
    """ Bot 主动离线事件 """
    bot_offline_event_active_switch: bool = False
    """ Bot 主动离线事件开关 """

    bot_offline_event_dropped: str = ""
    """ Bot 被挤下线事件 """
    bot_offline_event_dropped_switch: bool = False
    """ Bot 被挤下线事件开关 """

    bot_offline_event_force: str = "Bot {qq} 被服务器强制下线"
    """ Bot 被迫离线事件 """
    bot_offline_event_force_switch: bool = True
    """ Bot 被迫离线事件开关 """

    bot_online_event: str = ""
    """ Bot 上线事件 """
    bot_online_event_switch: bool = False
    """ Bot 上线事件开关 """

    bot_relogin_event: str = ""
    """ Bot 重连事件 """
    bot_relogin_event_switch: bool = False
    """ Bot 重连事件开关 """

    new_friend_request_event: str = (
        "收到好友申请\n"
        "\n事件 ID: {uuid}"
        "\n申请人: {supplicant}"
        "\n申请人昵称: {nickname}"
        "\n申请人留言: {message}"
        "\n来源群：{source_group}\n"
        "\n发送 #通过 {uuid} 以接受好友申请"
        "\n发送 #拒绝 {uuid} 以拒绝好友申请"
    )
    """ 新好友申请事件 """
    new_friend_request_event_switch: bool = True
    """ 新好友申请事件开关 """

    other_client_offline_event: str = ""
    """ 其他客户端下线事件 """
    other_client_offline_event_switch: bool = False
    """ 其他客户端下线事件开关 """

    other_client_online_event: str = ""
    """ 其他客户端上线事件 """
    other_client_online_event_switch: bool = False
    """ 其他客户端上线事件开关 """


@module_config(channel.module)
class _EventListenerGroupConfig:
    """事件监听器群组配置"""

    bot_group_permission_change_event: str = "Bot 的权限由 {origin_repr} 变更为 {current_repr}"
    """ 群权限变更事件 """
    bot_group_permission_change_event_switch: bool = True
    """ 群权限变更事件开关 """

    bot_join_group_event: str = ""
    """ Bot 加入群事件 """
    bot_join_group_event_switch: bool = True
    """ Bot 加入群事件开关 """

    bot_unmute_event: str = ""
    """ Bot 被取消禁言事件 """
    bot_unmute_event_switch: bool = True
    """ Bot 被取消禁言事件开关 """

    member_join_event: str = ""
    """ 群成员加入事件 """
    member_join_event_switch: bool = False
    """ 群成员加入事件开关 """

    member_join_request_event: str = (
        "收到入群申请\n"
        "\n事件 ID: {uuid}"
        "\n申请人: {supplicant}"
        "\n申请人昵称: {nickname}"
        "\n申请人留言: {message}"
        "\n申请群: {source_group}"
        "\n申请群名称: {group_name}\n"
        "\n发送 #通过 {uuid} 以接受入群申请"
        "\n发送 #拒绝 {uuid} 以拒绝入群申请"
    )
    """ 群成员加群申请事件 """
    member_join_request_event_switch: bool = True
    """ 群成员加群申请事件开关 """

    member_leave_event_kick: str = ""
    """ 群成员被踢事件 """
    member_leave_event_kick_switch: bool = False
    """ 群成员被踢事件开关 """

    member_leave_event_quit: str = ""
    """ 群成员主动离群事件 """
    member_leave_event_quit_switch: bool = False
    """ 群成员主动离群事件开关 """

    member_permission_change_event: str = ""
    """ 群成员权限改变事件 """
    member_permission_change_event_switch: bool = False
    """ 群成员权限改变事件开关 """


create(_EventListenerConfig)
module_create(_EventListenerGroupConfig, field=0)
module_save(_EventListenerGroupConfig)
