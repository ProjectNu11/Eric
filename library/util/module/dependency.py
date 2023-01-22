import subprocess
from pathlib import Path
from typing import NoReturn

from loguru import logger

from library.model.module import ModuleMetadata


def _get_requirements_by_module(module: ModuleMetadata) -> list[str]:
    requirements_path = Path(
        Path().resolve(), *module.pack.split("."), "requirements.txt"
    )
    return (
        requirements_path.read_text(encoding="utf-8").splitlines()
        if requirements_path.is_file()
        else []
    )


def install_dependency(
    module: ModuleMetadata = None, requirements: list[str] = None
) -> NoReturn:
    if not module and not requirements:
        raise ValueError("模块或依赖列表必须填写")
    if module:
        requirements = _get_requirements_by_module(module)

    command = ["pdm", "run", "pip", "install"]
    process = subprocess.Popen(
        [*command, *requirements],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    if info := stdout.decode("utf-8"):
        logger.info(info)
    if err := stderr.decode("utf-8"):
        logger.error(err)
