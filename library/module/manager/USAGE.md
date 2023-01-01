# {name} 管理器

## 控制模块开关

:::warning 需求权限

本指令需求最低权限：`群管理员`

:::

* 打开一个模块：`打开模块 <模块名>`
* 打开多个模块：`打开模块 <模块名1> <模块名2> <模块名3> ...`
* 关闭一个模块：`关闭模块 <模块名>`
* 关闭多个模块：`关闭模块 <模块名1> <模块名2> <模块名3> ...`

例：
```text
打开模块 Ping
关闭模块 事件监听器 系统状态
```

## 控制群组模块配置

:::warning 需求权限

本指令需求最低权限：`群管理员`

:::

* 列出所有模块配置：`{prefix}manager config list`
* 获取一个模块配置：`{prefix}manager config get <模块名>`
* 设置一个模块配置：`{prefix}manager config set <模块名> <配置名> = <配置值>`

例：
```text
{prefix}manager config get 事件监听器
{prefix}manager config set 事件监听器 member_join_request_event_switch = True
```

:::tip 仅有可分群配置的模块才会列出

部分模块的配置是全局的，无法分群配置，因此不会列出。

:::

## 控制模块仓库

:::warning 需求权限

本指令需求最低权限：`机器人所有人`

:::

* 注册一个模块仓库：`{prefix}manager register`，随后按照指引操作
* 更新一个模块仓库：`{prefix}manager update`

可 [在 Github 上搜索](https://github.com/search?q=EricPlugins) 合适的插件仓库

## 控制模块

:::warning 需求权限

本指令需求最低权限：`机器人所有人`

:::

* 安装一个模块：`{prefix}manager install [-y | --yes] <模块名>`
* 安装多个模块：`{prefix}manager install <模块名1> <模块名2> <模块名3> ...`
* 卸载一个模块：`{prefix}manager unload <模块名>`
* 卸载多个模块：`{prefix}manager unload <模块名1> <模块名2> <模块名3> ...`
* 更新所有模块：`{prefix}manager upgrade [-y | --yes]`

:::danger 注意

* 安装模块时，如果模块已经安装，将会自动卸载旧版本
* 如无法搜索到模块，可尝试使用模块的完整名称，或尝试 `{prefix}manager update` 更新缓存
* 部分模块无法进行卸载，通常情况下是因为该模块是必须模块

:::

## 跨群控制模块配置

:::warning 需求权限

本指令需求最低权限：`机器人所有人`

:::

* 获取一个模块配置：`{prefix}manager config get [-g | --group] <群号> <模块名>`
* 设置一个模块配置：`{prefix}manager config set [-g | --group] <群号> <模块名> <配置名> = <配置值>`
