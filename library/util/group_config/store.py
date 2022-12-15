from dataclasses import dataclass, field

from library.util.group_config.model import ModuleGroupConfig


@dataclass
class _GroupConfigStore:
    models: dict[str, type[ModuleGroupConfig]] = field(default_factory=dict)
    instances: dict[str, dict[int, ModuleGroupConfig]] = field(default_factory=dict)

    @property
    def mapping(self) -> dict[type[ModuleGroupConfig], str]:
        return {v: k for k, v in self.models.items()}


_store = _GroupConfigStore()
