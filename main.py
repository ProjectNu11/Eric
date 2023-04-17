import os
from pathlib import Path

import kayaku
from graia.ariadne import Ariadne
from loguru import logger

if __name__ == "__main__":
    os.environ["PYTHONUTF8"] = "1"
    if Path.cwd() != Path(__file__).parent:
        logger.warning("工作目录与项目目录不符，正在切换")
        os.chdir(Path(__file__).parent)
    kayaku.initialize({"{**}": "./config/{**}"})

    from library.service.stage import initialize

    initialize()
    Ariadne.launch_blocking()
