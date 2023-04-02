---
description: "在 Windows 上部署 Eric"
---

# 在 Windows 上部署 Eric

## 1. 前置条件

### 1.1. mirai

首先，你需要一个可以正常运行的 mirai 实例。如果你不知道如何部署 mirai，请参考
[Graia 官方文档](https://graia.cn/ariadne/appendix/mah-install/) 或
[Graia 社区文档](https://graiax.cn/before/install_mirai.html) 中的相关内容。

### 1.2. 如果你没有 Git

#### Step1 下载 git

- 官方低速下载 [Git for Windows](https://git-scm.com/download/win)

- 瓷器高速本地下载 [Git for Windows](https://webcdn.m.qq.com/spcmgr/download/Git-2.40.0-64-bit.exe)

- 巨硬下载 
``` bash
winget install --id Git.Git -e --source winget
```

#### Step2 安装 git

一路 next 即可 （嗯，就是这么简单）

#### Step3 验证安装

打开你的命令行工具（终端，powershell），输入以下命令，如果出现版本号，说明安装成功
``` bash
git --version
```
输出 belike

``` bash
git version 2.40.0.windows.1
```

### 1.3. 如果没有 Python3.10+

#### Step1 下载 Python （3.10.10）

- 官方低速下载 [Python](https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe)
- 瓷器霖念下载 [Python](https://river.linnian.icu/d/python-3.10.10-amd64.exe)
- 不推荐巨硬下载
- 不推荐西西下载园，ZOL下载，绿色资源网等等等等下载
- 不推荐 csdn 付费资源下载 （？）?😨


#### Step2 安装 Python

- 安装第一页，勾选 `Add Python.exe to path`,字有点小但是这一步很关键，不勾选的话，你的命令行工具（终端，powershell）无法识别 python 命令
- 使用 Customize installation 选项
- 勾选 'Install for all users'
- Next

#### Step3 验证安装

打开你的命令行工具（终端，powershell），输入以下命令，如果出现版本号，说明安装成功
``` bash
pip --version
```

OR

``` bash
python -m pip -V
```

输出 belike （不太一样没问题，确保结尾是 python3.10 及以上）

``` bash
pip 21.3.1 from c:\users\user\appdata\local\programs\python\python310\lib\site-packages\pip (python 3.10)
```

## 2. 下载

### 2.1. 下载 Eric

首先，你需要下载 Eric 的源代码。你可以通过以下方式下载：

- 通过 Git 下载（推荐）

    在终端中输入以下命令：

    ```bash
    git clone https://github.com/ProjectNu11/Eric.git
    ```

    随后，你可以通过 `cd Eric` 命令进入 Eric 的目录并继续操作。

- 通过 GitHub 下载

    你可以通过 GitHub 直接下载 Eric 的源代码。点击
    [这里](https://github.com/ProjectNu11/Eric/archive/refs/heads/main.zip)
    下载 Eric 的源代码归档文件。

    ~~随后，你可以通过 `unzip Eric-main.zip` 命令解压 Eric 的源代码归档文件并继续操作~~
    
    都用 Win 了，别告诉我你不会解压。

!!! warning "建议使用 Git 下载"

    如源代码并非使用 `git clone` 命令下载，Eric 内置的自动更新将不再可用，
    你可能需要自行更新问题。

## 3. 安装依赖

### 3.1. 初始化虚拟环境

Eric 使用了 `PDM` 来管理依赖。

!!! warning "Eric 将不再支持 `poetry`，请使用 `PDM` 进行安装"

#### 3.1.1. 安装 `pdm`

首先，你需要安装 `pdm`。你可以通过以下方式安装：

- 通过脚本安装（推荐）

    在终端中输入以下命令：

    ```bash
    (Invoke-WebRequest -Uri https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py -UseBasicParsing).Content | python -
    ```


- 通过 `pip` 安装

    在终端中输入以下命令：

    ```bash
    pip install pdm
    ```

!!! warning "建议使用脚本安装"

    某些情况下，使用 `pip` 直接安装 `pdm` 可能会影响当前 `Python` 环境安装的依赖出现冲突。


#### 3.1.2. 安装依赖

在终端中输入以下命令即可安装 Eric 的依赖：

```bash
pdm install
```

??? question "需要修改 `pdm` 使用的 Python 版本？"

    如果你需要修改 `pdm` 使用的 Python 版本，请使用以下命令：

    ```bash
    pdm use <python_path>
    ```

    其中，`<python_path>` 为你需要使用的 Python 的路径或版本号，
    如 `python3.10` 或 `/usr/bin/python3.10`。

## 4. 配置

初次运行 Eric 时，你需要配置 Eric。

在终端中输入以下命令生成空白配置文件：

```bash
pdm run start
```

随后，你应可以在 `config` 文件夹中找到生成的空白配置文件，按照你的需求修改 `.jsonc` 文件即可。

## 5. 运行

在终端中输入以下命令即可运行 Eric：

```bash
pdm run start
```

你应可以在终端中看到 Eric 的输出：

```text
2022-12-09 10:17:47.858 | SUCCESS  | library.config.validate:validate_config:94 - 配置验证通过
2022-12-09 10:17:47.917 | SUCCESS  | library.config.initialize:_bootstrap:48 - 配置初始化完成
2022-12-09 10:17:48.154 | SUCCESS  | library.util.module:resolve:77 - [Modules] 解析模块依赖完成
2022-12-09 10:17:48.154 | SUCCESS  | library.util.module.launch:launch_require:22 - [EricService] 已校验 9 个模块
2022-12-09 10:17:48.194 | INFO     | graia.saya:require:134 - module loading finished: library.module.file_server
2022-12-09 10:17:48.226 | INFO     | graia.saya:require:134 - module loading finished: library.module.ping
2022-12-09 10:17:48.516 | INFO     | graia.saya:require:134 - module loading finished: library.module.executor
2022-12-09 10:17:48.743 | INFO     | graia.saya:require:134 - module loading finished: library.module.system_status
2022-12-09 10:17:48.749 | INFO     | graia.saya:require:134 - module loading finished: library.module.exchange
2022-12-09 10:17:48.770 | INFO     | graia.saya:require:134 - module loading finished: library.module.help
2022-12-09 10:17:49.380 | INFO     | graia.saya:require:134 - module loading finished: library.module.exception_handler
2022-12-09 10:17:49.450 | INFO     | graia.saya:require:134 - module loading finished: library.module.manager
2022-12-09 10:17:49.459 | WARNING  | library.util.module.require:_require_install_deps:30 - 未指定 --console
2022-12-09 10:17:49.588 | INFO     | launart.manager:launch_blocking:446 - Starting launart main task...
2022-12-09 10:17:49.590 | INFO     | launart.manager:launch:313 - Launching 11 components as async task...
2022-12-09 10:17:49.704 | INFO     | graia.ariadne.service:base_telemetry:142 -
    _         _           _
   / \   _ __(_) __ _  __| |_ __   ___
  / _ \ | '__| |/ _` |/ _` | '_ \ / _ \
 / ___ \| |  | | (_| | (_| | | | |  __/
/_/   \_\_|  |_|\__,_|\__,_|_| |_|\___|

graiax-fastapi: 0.2.1
graiax-playwright: 0.2.1
graiax-text2img-playwright: 0.2.0
graia-amnesia: 0.7.0
graia-ariadne: 0.10.0
graia-broadcast: 0.19.0
graia-saya: 0.0.17
graia-scheduler: 0.0.10
kayaku: 0.5.0
launart: 0.6.1
statv: 0.3.2
```

至此，Eric 已经启动成功。