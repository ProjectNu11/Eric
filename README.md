<div align="center">

# Eric

_Let go of it all._

[//]: # (Let go of it all, close your eyes, and sink into this bottomless pool.)

> [ ]

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Python version: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/624187ab6cd5409188dd86fcfe9f0443)](https://www.codacy.com/gh/nullqwertyuiop/Eric/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=nullqwertyuiop/Eric&amp;utm_campaign=Badge_Grade)
[![DeepSource](https://deepsource.io/gh/nullqwertyuiop/Eric.svg/?label=active+issues&token=B3VBW5DBd_og4EPma6Cgk3E7)](https://deepsource.io/gh/nullqwertyuiop/Eric/?ref=repository-badge)

</div>

本项目仍处于开发阶段，暂不建议部署。

## 目录
  * [目录](#目录)
  * [项目特色](#项目特色)
  * [开始使用](#开始使用)
  * [使用文档](#使用文档)
  * [注意](#注意)
  * [项目结构](#项目结构)
  * [参与贡献](#参与贡献)
  * [许可证](#许可证)
  * [鸣谢](#鸣谢)

## 项目特色

  * 在线插件仓库
  * 基于 SQLAlchemy 的异步 ORM
  * 多账号支持

## 开始使用

## 使用文档

## 注意

## 项目结构

```
Eric
├── config ······················ (*) 配置文件
│   ├── group_config ············ (*) 群组配置
│   ├── library ················· (*) 库配置
│   ├── module ·················· (*) 模块配置
│   ├── config.jsonc ············ (*) 主配置
│   └── config.schema.json ······ (*) 主配置模式
├── data ························ (*) 运行数据
│   ├── library ················· (*) 库数据
│   ├── module ·················· (*) 模块数据
│   ├── shared ·················· (*) 共享数据
│   ├── temp ···················· (*) 临时数据
│   └── data.db ················· (*) 数据库
├── library ·····················     程序主体
│   ├── assets ··················     资源文件
│   ├── config ··················     配置模块
│   ├── decorator ···············     装饰器模块
│   ├── model ···················     数据模型模块
│   ├── module ··················     库模块
│   ├── service ·················     服务模块
│   ├── ui ······················     图形界面
│   ├── util ····················     工具模块
│   └── __init__.py ·············     入口模块
├── log ························· (*) 运行日志
├── module ······················ (*) 已安装模块
├── LICENSE ·····················     许可证
├── main.py ·····················     程序入口
├── poetry.lock ·················     依赖锁定文件
├── pyproject.toml ··············     项目依赖 (Poetry)
└── README.md ···················     项目说明

* 表示该文件或文件夹在以默认配置运行时会被自动创建
```

## 参与贡献

你可以通过以下方式参与到本项目中：

  * 提交 [Issue](https://github.com/nullqwertyuiop/Eric/issues)
  * 提交 [Pull Request](https://github.com/nullqwertyuiop/Eric/pulls)

## 许可证

    Copyright (C) 2022 nullqwertyuiop

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

## 鸣谢

### 框架

  * [mirai](https://github.com/mamoe/mirai), 高效率 QQ 机器人框架 / High-performance bot framework for Tencent QQ
  * [mirai-api-http](https://github.com/project-mirai/mirai-api-http), Mirai HTTP API (console) plugin
  * [Graia Ariadne](https://github.com/GraiaProject/Ariadne), 一个优雅且完备的 Python QQ 自动化框架。基于 Mirai API HTTP v2。

### Bot 项目

  * [Null (Depr.)](https://github.com/ProjectNu11/Project-Null), 本项目的前身
  * [SAGIRI-BOT](https://github.com/SAGIRI-kawaii/sagiri-bot), 一个基于 Mirai 和 Graia-Ariadne 的QQ机器人
