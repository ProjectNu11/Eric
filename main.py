import os
import sys
from pathlib import Path

import kayaku
from graia.ariadne import Ariadne

if __name__ == "__main__":
    os.environ["PYTHONUTF8"] = "1"

    if Path.cwd() != Path(__file__).parent:
        os.chdir(Path(__file__).parent)

    kayaku.initialize({"{**}": "./config/{**}"})
    with_console = "--console" in sys.argv

    from library.service.stage import initialize

    initialize(with_console=with_console)
    Ariadne.launch_blocking()
