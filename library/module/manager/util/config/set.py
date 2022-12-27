import inspect
from typing import TypeVar

from graia.ariadne.model import Group

from library.model.module import Module
from library.module.manager.util.config.util import _pre_check, get_module_config
from library.util.group_config.model import ModuleGroupConfig
from library.util.group_config.util import module_save

_T = TypeVar("_T")


def _cast_bool(value: str) -> bool:
    if value in {"true", "True", "1"}:
        return True
    if value in {"false", "False", "0"}:
        return False
    raise ValueError(f"Invalid bool value: {value}")


def _cast(value: str, type_: _T) -> _T:
    # Assume type_ is a simple type such as int, float, str, bool
    return _cast_bool(value) if type_ is bool else type_(value)


def _set(
    config: ModuleGroupConfig, **kwargs
) -> tuple[list[tuple[str, str]], list[str], list[tuple[str, str]]]:
    anno: dict[str, type] = inspect.get_annotations(type(config))
    success: list[tuple[str, str]] = []
    not_found: list[str] = [k for k in kwargs if k not in anno]
    failed: list[tuple[str, str]] = []
    for k, v in kwargs.items():
        if k in not_found:
            continue
        try:
            setattr(config, k, _cast(v, anno[k]))
            success.append((k, v))
        except AssertionError as e:
            failed.append((k, e.args[0]))
        except Exception as e:
            failed.append((k, str(e)))
    return success, not_found, failed


def _get_msg_success(success: list[tuple[str, str]]) -> str:
    if not success:
        return ""
    text = f"{len(success)} 个配置项设置成功"
    for k, v in success:
        text += f"\n - {k}: {v}"
    return text


def _get_msg_not_found(not_found: list[str]) -> str:
    if not not_found:
        return ""
    text = f"{len(not_found)} 个配置项不存在"
    for k in not_found:
        text += f"\n - {k}"
    return text


def _get_msg_failed(failed: list[tuple[str, str]]) -> str:
    if not failed:
        return ""
    text = f"{len(failed)} 个配置项设置失败"
    for k, v in failed:
        text += f"\n - {k}: {v}"
    return text


def _get_msg(
    module: Module,
    field: int | Group,
    success: list[tuple[str, str]],
    not_found: list[str],
    failed: list[tuple[str, str]],
) -> str:
    text = f"{module.name} 配置 ({int(field)})\n"
    msgs = [
        _get_msg_success(success),
        _get_msg_not_found(not_found),
        _get_msg_failed(failed),
    ]
    text += "\n".join(msg for msg in msgs if msg)
    return text


def mgr_set_module_config(field: Group | int, mod: str, **kwargs) -> str:
    module = _pre_check(mod)
    config = get_module_config(field, module)
    module_save(type(config), field=field)
    success, not_found, failed = _set(config, **kwargs)
    return _get_msg(module, field, success, not_found, failed)
