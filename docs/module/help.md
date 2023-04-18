---
description: "帮助菜单"
---

# 帮助菜单

该模块用于显示帮助菜单。

## tldr

| 命令      | 参数            | 说明                 |
|:--------|:--------------|:-------------------|
| `.help` |               | 显示帮助菜单             |

| 路径                                            | 参数            | 说明                 |
|:----------------------------------------------|:--------------|:-------------------|
| `/service/help/index`                         |               | 显示帮助菜单             |
| `/service/help/module/get/{pack}`             | `pack`        | 显示模块帮助             |
| `/service/help/module/markdown/{pack}/{file}` | `pack` `file` | 显示模块下的 markdown 文件 |
| `/service/help/module/search/{keyword}`       | `keyword`     | 依照关键字搜索模块          |
| `/service/help/category/search/{category}`    | `category`    | 依照分类搜索模块           |

## 显示帮助菜单（`.help`）

可直接发送 `.help` 命令来显示已渲染的帮助菜单。

## 显示模块帮助（`/service/help/module/get/{pack}`）

可通过 `/service/help/module/get/{pack}` 来显示模块帮助。

该接口会返回已转换为 HTML 的帮助菜单。

| 参数     | 类型       | 说明   |
|:-------|:---------|:-----|
| `pack` | `string` | 模块包名 |

!!! info "大部分情况下无需手动使用以下接口"

    以下接口一般用于 `Playwright` 等渲染，或已由主菜单链接，无需手动使用。

## 显示模块下的 markdown 文件

可通过 `/service/help/module/markdown/{pack}/{file}` 来显示模块下的 markdown 文件。

该接口会返回已转换为 HTML 的 markdown 文件。

| 参数     | 类型       | 说明   |
|:-------|:---------|:-----|
| `pack` | `string` | 模块包名 |

## 依照关键字搜索模块

可通过 `/service/help/module/search/{keyword}` 来依照关键字搜索模块。

该接口会返回已转换为 HTML 的搜索结果。

| 参数        | 类型       | 说明    |
|:----------|:---------|:------|
| `keyword` | `string` | 搜索关键字 |

## 依照分类搜索模块

可通过 `/service/help/category/search/{category}` 来依照分类搜索模块。

该接口会返回已转换为 HTML 的搜索结果。

| 参数         | 类型       | 说明   |
|:-----------|:---------|:-----|
| `category` | `string` | 搜索分类 |
