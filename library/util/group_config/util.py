import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, TypeVar, cast

import kayaku
from graia.ariadne.model import Group
from typing_extensions import dataclass_transform

from library.model.config.path import PathConfig
from library.util.group_config.model import ModuleGroupConfig
from library.util.group_config.store import _store

_T = TypeVar("_T")
cfg: PathConfig = kayaku.create(PathConfig)
CONFIG_PATH = Path(cfg.config) / "group_config"


@dataclass_transform()
def _cfg_stub(module: str, **kwargs) -> Callable[[type[_T]], type[_T]]:  # noqa
    """
    将类型转换为 Eric 的配置类型

    Args:
        module: 模块名
        kwargs: dataclass 的参数

    Returns:
        转换后的类型
    """
    ...


def _cfg_impl(module: str, **kwargs) -> Callable[[type[_T]], type[ModuleGroupConfig]]:
    def wrapper(cls: type[_T]) -> type[ModuleGroupConfig]:
        cls = cast(type[ModuleGroupConfig], dataclass(**kwargs)(cls))
        _store.models[module] = cls
        return cls

    return wrapper


def _from_file(module: str, field: int) -> ModuleGroupConfig:
    config_cls = _store.models[module]
    field_path = CONFIG_PATH / str(field)
    field_path.mkdir(parents=True, exist_ok=True)
    config_path = field_path / f"{module}.json"
    if not config_path.exists():
        return config_cls()
    with config_path.open("r", encoding="utf-8") as f:
        data = json.loads(f.read())
    return config_cls(**data)


def module_create(cls: type[_T], field: int | Group, flush: bool = False) -> _T:
    """
    创建模块配置

    Args:
        cls: 模块配置类
        field: 群号
        flush: 是否强制刷新

    Raises:
        TypeError: 如果 cls 未注册
    """
    if not (issubclass(cls, ModuleGroupConfig)) or cls not in _store.mapping:
        raise TypeError(f"{cls!r} is not a registered ConfigModel class!")
    module = _store.mapping[cls]
    field = int(field)
    if not flush and field in _store.instances.get(module, {}):
        return _store.instances[module][field]
    config = _from_file(module, field)
    _store.instances.setdefault(module, {})[field] = config
    return cast(_T, config)


def _module_save_single(module: str, field: int, data: dict):
    with (CONFIG_PATH / str(field) / f"{module}.json").open("w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))


def module_save(model: type[_T], *, field: int = None):
    """
    保存模块配置

    Args:
        model: 模块配置类
        field: 群号，如果为 None 则保存所有群的配置

    Raises:
        TypeError: 如果 model 未注册
    """
    if model not in _store.mapping:
        raise TypeError(f"{model!r} is not a registered ConfigModel class!")
    module = _store.mapping[model]
    if field is not None:
        assert (
            field in _store.instances[module]
        ), f"Model {model!r} is not initialized for {field}!"
        _module_save_single(module, field, _store.instances[module][field].__dict__)
        return
    for field, config in _store.instances[module].items():
        _module_save_single(module, field, config.__dict__)


def module_save_all():
    """
    保存所有模块配置
    """
    for module, instances in _store.instances.items():
        for field, config in instances.items():
            _module_save_single(module, field, config.__dict__)


module_config = _cfg_stub if TYPE_CHECKING else _cfg_impl
