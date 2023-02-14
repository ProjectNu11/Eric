import re
from typing import Generator, Iterable, TypeVar

from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.model import MemberPerm

from library.model.permission import UserPerm
from library.util.typ import FieldWide

_T = TypeVar("_T")


def seconds_to_string(
    time: int | float,
    *,
    repr_ms: bool = True,
    ms_accuracy: int = 2,
    zh_cn: bool = True,
) -> str:
    """
    将秒数转换为字符串

    Args:
        time: 秒数
        repr_ms: 是否显示毫秒
        ms_accuracy: 毫秒精度
        zh_cn: 是否使用中文

    Returns:
        转换后的字符串
    """
    seconds, ms = divmod(time, 1)
    minutes, seconds = divmod(time, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    months, weeks = divmod(weeks, 4)
    years, months = divmod(months, 12)
    seconds = int(seconds)
    interval_repr = f"{seconds:02d}{' 秒' if zh_cn else 's'}"
    if ms and repr_ms:
        interval_repr += (
            f" {str(int(ms * 1000))[:ms_accuracy]}{' 毫秒' if zh_cn else 'ms'}"
        )
    if minutes := int(minutes):
        interval_repr = f"{minutes:02d}{' 分' if zh_cn else 'm'} {interval_repr}"
    if hours := int(hours):
        interval_repr = f"{hours:02d}{' 时' if zh_cn else 'h'} {interval_repr}"
    if days := int(days):
        interval_repr = f"{days}{' 天' if zh_cn else 'd'} {interval_repr}"
    if weeks := int(weeks):
        interval_repr = f"{weeks}{' 周' if zh_cn else 'w'} {interval_repr}"
    if months := int(months):
        interval_repr = f"{months}{' 月' if zh_cn else 'M'} {interval_repr}"
    if years := int(years):
        interval_repr = f"{years}{' 年' if zh_cn else 'y'} {interval_repr}"
    return interval_repr


def inflate(*obj: Iterable[_T]) -> list[_T]:
    """
    将多个可迭代对象合并为一个列表

    Args:
        obj: 可迭代对象

    Returns:
        合并后的列表
    """
    result = []
    for o in obj:
        if isinstance(o, Generator):
            o = list(o)
        if isinstance(o, (tuple, list, set)):
            result.extend(inflate(*o))
        else:
            result.append(o)
    return result


QUOTE_PATTERN = re.compile(r"""(".+?"|'.+?'|[^ "']+)""")


def camel_to_snake(name: str) -> str:
    """
    将驼峰命名法转换为下划线命名法

    Args:
        name: 驼峰命名法字符串

    Returns:
        下划线命名法字符串
    """
    return "_".join(re.sub(r"([A-Z])", r"_\1", name).lower().split("_")).strip("_")


PERMISSION_MAPPING: dict[UserPerm | MemberPerm, str] = {
    UserPerm.BLOCKED: UserPerm.BLOCKED.value[-1],
    UserPerm.BOT: UserPerm.BOT.value[-1],
    UserPerm.MEMBER: UserPerm.MEMBER.value[-1],
    UserPerm.ADMINISTRATOR: UserPerm.ADMINISTRATOR.value[-1],
    UserPerm.OWNER: UserPerm.OWNER.value[-1],
    UserPerm.BOT_ADMIN: UserPerm.BOT_ADMIN.value[-1],
    UserPerm.BOT_OWNER: UserPerm.BOT_OWNER.value[-1],
    UserPerm.INFINITE: UserPerm.INFINITE.value[-1],
    MemberPerm.Member: "普通成员",
    MemberPerm.Administrator: "管理员",
    MemberPerm.Owner: "群主",
}


def extract_field(event: MessageEvent) -> FieldWide:
    return event.sender.group if isinstance(event, GroupMessage) else 0
