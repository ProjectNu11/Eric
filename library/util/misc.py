import re


def seconds_to_string(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    interval_repr = f"{seconds:02d} 秒"
    if minutes:
        interval_repr = f"{minutes:02d} 分 {interval_repr}"
    if hours:
        interval_repr = f"{hours:02d} 时 {interval_repr}"
    return interval_repr


def inflate(*obj) -> list:
    result = []
    for o in obj:
        if isinstance(o, (tuple, list)):
            result.extend(inflate(*o))
        else:
            result.append(o)
    return result


QUOTE_PATTERN = re.compile(r"""(".+?"|'.+?'|[^ "']+)""")
