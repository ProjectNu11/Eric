import os
from datetime import datetime

import psutil
from launart import Launart, Launchable
from rich.table import Table
from rich.text import Text

from library.model import ModuleMetadata, RequireStatus
from library.util.ctx import rich_console

_code_map: dict[RequireStatus, Text] = {
    RequireStatus.SUCCESS: Text("正常", style="green"),
    RequireStatus.SKIPPED: Text("跳过加载", style="yellow"),
    RequireStatus.MISSING_DEPENDENCY: Text("缺少依赖", style="magenta"),
    RequireStatus.ERROR: Text("意外错误", style="red"),
}

_launch_time: dict[ModuleMetadata, tuple[float, RequireStatus]] = {}


def add_launch_time(module: ModuleMetadata, _time: float, status: RequireStatus):
    _launch_time[module] = (_time, status)


class LaunchTimeService(Launchable):
    id = "eric.util.launch_time"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, _mgr: Launart):
        async with self.stage("blocking"):
            current_proc = psutil.Process(os.getpid())
            create_time = datetime.fromtimestamp(current_proc.create_time())
            delta = datetime.now() - create_time
            module_sum = sum(_time for _time, _ in _launch_time.values())

            title = (
                Text("本次启动耗时 ", style="red")
                .append(Text(str(delta.total_seconds()), style="yellow"))
                .append(Text(" 秒，模块加载耗时 ", style="red"))
                .append(Text(str(module_sum), style="yellow"))
                .append(Text(" 秒", style="red"))
            )

            table = Table(title=title)
            table.add_column("模块")
            table.add_column("耗时")
            table.add_column("状态")

            for module, (_time, code) in sorted(
                _launch_time.items(), key=lambda x: x[1], reverse=True
            ):
                table.add_row(
                    Text(module.clean_name),
                    Text(str(_time), style="yellow"),
                    _code_map[code],
                )

            rich_console.get().print()
            rich_console.get().print(table)
