---
description: "主配置文件"
---

# 主配置文件

主配置文件位于 `config/config.jsonc`，负责配置 Eric 的核心部分。

| 字段名               | 类型          | 默认值      | 说明                              |
|:------------------|:------------|:---------|:--------------------------------|
| `name`            | `str`       | `Eric`   | 机器人的名称                          |
| `accounts`        | `list[int]` | `[]`     | 机器人的账号列表，不可为空                   |
| `default_account` | `int`       | `0`      | 机器人使用的默认账号                      |
| `description`     | `str`       | `""`     | 机器人的描述，用于显示在帮助信息中               |
| `environment`     | `str`       | `poetry` | 机器人的运行环境，可选 `poetry` 或 `pip`    |
| `host`            | `str`       | `""`     | `mirai-api-http` 的地址            |
| `verify_key`      | `str`       | `""`     | `mirai-api-http` 的认证密钥          |
| `owners`          | `list[int]` | `[]`     | 机器人的所有者 QQ 号列表，用于分配权限           |
| `dev_groups`      | `list[int]` | `[]`     | 机器人的开发者群号列表                     |
| `debug`           | `bool`      | `False`  | 是否开启调试模式                        |
| `proxy`           | `str`       | `""`     | 代理地址，格式为 `protocol://host:port` |
| `log_rotate`      | `int`       | `7`      | 日志文件的切割周期                       |
| `$schema`         | `str`       | 自动生成     | JSON Schema 的地址，请勿修改            |
