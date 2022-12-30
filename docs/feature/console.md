---
description: "控制台支持"
---

# 控制台支持

Eric 支持使用 `ConsoleSchema`，提供了一个简单的控制台。

!!! danger "`ConsoleSchema` 是已被 `Graia Ariadne` 废弃的特性"

    使用时可能出现未预期的问题，建议仅在无法通过 QQ 与机器人交互时使用。

!!! note "控制台不会默认启动"

    需要添加启动参数 `--console` 才能启动控制台。

    如 `poetry run python main.py --console`

!!! danger "开启控制台后无法使用 ++ctrl+c++ 退出"

    需自行在控制台输入 `exit` 确认并退出。
