---
description: "FastAPI 配置"
---

# FastAPI 配置

主配置文件位于 `config/library/service/fastapi.jsonc`，负责配置 Eric 的 FastAPI 实例。

| 字段名         | 类型                                       | 默认值         | 说明                                                                                  |
|:------------|:-----------------------------------------|:------------|:------------------------------------------------------------------------------------|
| `host`      | `str`                                    | `127.0.0.1` | FastAPI 的监听地址                                                                       |
| `port`      | `int`                                    | `8000`      | FastAPI 的监听端口                                                                       |
| `domain`    | `str`                                    | `""`        | FastAPI 的域名，仅在发送消息中使用                                                               |
| `params`    | `dict[str, typing.Optional[typing.Any]]` | `{}`        | FastAPI 的额外参数，详见 [FastAPI 文档](https://fastapi.tiangolo.com/advanced/extra-options/) |
| `show_port` | `bool`                                   | `true`      | 是否在发送消息中展示端口                                                                        |
| `https`     | `bool`                                   | `true`      | 发送的链接是否使用 `https` 协议                                                                |
