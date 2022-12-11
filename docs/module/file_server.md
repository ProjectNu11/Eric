---
description: "文件服务器"
---

# 文件服务器

该模块用于提供文件服务器功能，服务器的 Base URL 需要在配置文件中设置。

## tldr

| 路径                             | 参数              | 说明              |
|:-------------------------------|:----------------|:----------------|
| `/service/file/{file_id}`      | `file_id`       | 通过文件 ID 获取文件    |
| `/assets/library/{file:path}`  | `file`          | 通过文件路径获取库的资源文件  |
| `/assets/{module}/{file:path}` | `module` `file` | 通过文件路径获取模块的资源文件 |

## 通过文件 ID 获取文件

通过文件 ID 获取文件，文件 ID 为随机不重复的 UUID。

路径：`/service/file/{file_id}`

| 参数        | 类型       | 说明    |
|:----------|:---------|:------|
| `file_id` | `string` | 文件 ID |

## 通过文件路径获取库的资源文件

通过文件路径获取库的资源文件，文件路径为相对于 `library/assets` 目录的路径。

路径：`/assets/library/{file:path}`

| 参数     | 类型       | 说明   |
|:-------|:---------|:-----|
| `file` | `string` | 文件路径 |

## 通过文件路径获取模块的资源文件

通过文件路径获取模块的资源文件，文件路径为相对于 `modules/{module}/assets` 目录的路径。

路径：`/assets/{module}/{file:path}`

| 参数       | 类型       | 说明   |
|:---------|:---------|:-----|
| `module` | `string` | 模块包名 |
| `file`   | `string` | 文件路径 |
