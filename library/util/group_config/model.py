from abc import ABC
from dataclasses import Field, is_dataclass
from typing import ClassVar


class ModuleGroupConfig(ABC):
    __dataclass_fields__: ClassVar[dict[str, Field]]

    @classmethod
    def __subclasshook__(cls, oth):
        return isinstance(oth, type) and is_dataclass(oth)
