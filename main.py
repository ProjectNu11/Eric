def setup():
    import os
    from pathlib import Path

    from loguru import logger

    os.environ["PYTHONUTF8"] = "1"
    if Path.cwd() != Path(__file__).parent:
        logger.warning("工作目录与项目目录不符，正在切换")
        os.chdir(Path(__file__).parent)

    import kayaku

    kayaku.initialize({"{**}": "./config/{**}"})


if __name__ == "__main__":
    setup()

    from graia.ariadne import Ariadne

    from library.service.stage import initialize

    initialize()
    Ariadne.launch_blocking()
