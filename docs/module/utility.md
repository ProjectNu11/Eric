---
description: "实用工具"
---

# 实用工具

## tldr

| 命令                        | 说明          | 需求最低权限 |
|:--------------------------|:------------|:-------|
| `[@bot] shell> <command>` | 用于执行终端命令    | 机器人所有人 |
| `.ping`                   | 用于测试机器人是否在线 | 任何人    |
| `.sys`                    | 用于查看机器人系统信息 | 机器人管理员 |

## 执行终端命令

拥有机器人所有人权限的用户可以通过 `[@bot] shell>` 命令执行终端命令。

例如，执行 `[@bot] shell> ls` 命令，将会在终端中执行 `ls` 命令，并将结果渲染完成后返回给用户。

| 参数          | 说明     |
|:------------|:-------|
| `[@bot]`    | At 机器人 |
| `<command>` | 终端命令   |

## 测试机器人是否在线

用于测试机器人是否在线，直接发送 `.ping` 即可，账号已登录时会回复 `pong`。

## 查看机器人系统信息

用于查看机器人系统信息，直接发送 `.sys` 即可，账号已登录时会回复已渲染为图片的机器人系统信息。