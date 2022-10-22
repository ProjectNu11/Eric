import contextlib
from json import JSONDecodeError
from pathlib import Path

from loguru import logger
from pydantic import ValidationError

from library.model.module import ModuleMetadata


def parse_metadata(module: Path) -> ModuleMetadata:
    try:
        return ModuleMetadata.parse_file(module / "metadata.json")
    except ValidationError as e:
        logger.error(f"模块 {module} 的元数据不符合规范")
        logger.error(e.with_traceback(e.__traceback__))
        raise e


def generate_metadata(module: Path) -> ModuleMetadata:
    name = module.parts[-1]
    pack = ".".join(module.parts)
    return ModuleMetadata(name=name, pack=pack)


def write_metadata(metadata: ModuleMetadata):
    module_path = Path(metadata.pack.replace(".", "/"))
    with (module_path / "metadata.json").open("w") as f:
        f.write(metadata.json(indent=4, ensure_ascii=False))
        # Trailing new line to prevent pre-commit from complaining
        f.write("\n")


def update_metadata(module: Path) -> ModuleMetadata:
    with contextlib.suppress(FileNotFoundError, ValidationError, JSONDecodeError):
        new = parse_metadata(module)
        write_metadata(new)
        return new
    new = generate_metadata(module)
    write_metadata(new)
    return new
