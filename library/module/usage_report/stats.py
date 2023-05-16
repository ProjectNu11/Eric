import itertools
from datetime import datetime, timedelta

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Forward, ForwardNode
from kayaku import create
from sqlalchemy import select

from library.model import EricConfig
from library.util.module import Modules
from library.util.orm import orm
from library.util.orm.table import FunctionCallRecord
from library.util.typ import Sender

RECORD_TYPE = tuple[datetime, int, int, str]
name = create(EricConfig).name


async def fetch_stats(
    supplicant: int,
    field: int | None = None,
    time_left: datetime = None,
    time_right: datetime = None,
) -> list[RECORD_TYPE]:
    time_left = time_left or datetime(datetime.now().year, 1, 1)
    time_right = time_right or datetime.now()
    conditions = [
        FunctionCallRecord.time >= time_left,
        FunctionCallRecord.time < time_right,
        FunctionCallRecord.supplicant == supplicant,
    ]
    if field is not None:
        conditions.append(FunctionCallRecord.field == field)
    return await orm.all(
        select(
            FunctionCallRecord.time,
            FunctionCallRecord.field,
            FunctionCallRecord.supplicant,
            FunctionCallRecord.function,
        ).where(*conditions)
    )


def parse_module_name(pack: str) -> str:
    return mod.name if (mod := it(Modules).get(pack)) else pack


def parse_by_latest(data: list[RECORD_TYPE]) -> list[str]:
    parsed = filter(
        lambda x: (datetime((d := x[0]).year, d.month, d.day, 5) - d).total_seconds()
        >= 0,
        data,
    )
    parsed = sorted(
        parsed,
        key=lambda x: (
            datetime((d := x[0]).year, d.month, d.day, 5) - d
        ).total_seconds(),
    )
    return (
        [
            f"{parsed[0][0].strftime('%m月%d日')} 你睡得很晚\n"
            f"{parsed[0][0].strftime('%H点%M分')} 还在使用 "
            f"{parse_module_name(parsed[0][3])}"
        ]
        if parsed
        else [f"你似乎没有在半夜使用过{name}\n早睡早起身体好"]
    )


def parse_per_day(data: list[RECORD_TYPE]) -> list[str]:
    parsed = itertools.groupby(data, key=lambda x: x[0].date())
    parsed = {k: list(v) for k, v in parsed}
    max_day = max(parsed.items(), key=lambda x: len(list(x[1])))
    return [
        f"{max_day[0].strftime('%m月%d日')}\n你使用 " f"{name} 达到了 {len(list(max_day[1]))} 次"
    ]


def parse_per_module(data: list[RECORD_TYPE], scale: str) -> list[str]:
    # 不知道为什么但是它就是没有预期效果
    # parsed = itertools.groupby(data, key=lambda x: x[3].split(":")[0])
    # parsed = {k: list(v) for k, v in parsed}
    parsed: dict[str, list[RECORD_TYPE]] = {}
    for d in data:
        parsed.setdefault(d[3].split(":")[0], []).append(d)
    max_module = max(parsed.items(), key=lambda x: len(list(x[1])))
    result = [
        f"{scale}你一共使用过\n{len(data)} 次 {name}\n{len(parsed.keys())} 个模块",
        f"陪伴你最多的模块是 {parse_module_name(max_module[0])}\n"
        f"它{scale}被你使用了 {len(list(max_module[1]))} 次",
    ]
    top_list = [f"你的{scale[-1]}度榜单"]
    top_list.extend(
        f"{index + 1}. {parse_module_name(mod_name)} [{len(mod_data)} 次]"
        for index, (mod_name, mod_data) in enumerate(
            sorted(parsed.items(), key=lambda x: len(list(x[1])), reverse=True)[:10]
        )
    )
    result.append("\n".join(top_list))
    return result


def parse_all(data: list[RECORD_TYPE], scale: str) -> list[str]:
    return (
        parse_by_latest(data.copy())
        + parse_per_day(data.copy())
        + parse_per_module(data.copy(), scale)
    )


async def get_report(app: Ariadne, supplicant: Sender) -> MessageChain:
    data = await fetch_stats(int(supplicant))
    parsed = parse_all(data, "今年")
    return MessageChain(
        Forward(
            ForwardNode(
                target=app.account,
                time=datetime.now() - timedelta(minutes=len(parsed) - index),
                message=MessageChain(part),
                name=name,
            )
            for index, part in enumerate(parsed)
        )
    )
