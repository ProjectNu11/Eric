---
description: "数据库配置"
---

主配置文件位于 `config/databse.jsonc`，负责配置 Eric 的 ORM。

| 字段名    | 类型    | 默认值                                | 说明       |
|:-------|:------|:-----------------------------------|:---------|
| `link` | `str` | `sqlite+aiosqlite:///data/data.db` | 数据库的链接地址 |

!!! warning "关于数据库链接配置"

    大部分情况下保持不变即可。

    如需要指定使用的数据库或使用 `MySQL` 等，则需要更改至相应链接，格式如下：

    * `SQLite`

        > `sqlite+aiosqlite:///data/data.db`

        > 使用该链接将使用 Eric 部署目录下的 data/data.db

        > 链接必须以 `sqlite+aiosqlite://` 开头，否则将无法正常使用

    * `MySQL`

        > `mysql+aiomysql://username:password@ip:port/database`

        > 使用该链接将以 `username` 为用户名，`password` 为密码连接至位于 `ip:port` 的 `database` 数据库

        > 链接必须以 `mysql+aiomysql://` 开头，否则将无法正常使用

    * 其他数据库

        > 暂不支持

    **如果你看不懂上述文本的话保持不变即可。**
