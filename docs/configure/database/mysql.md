---
description: "MySQL 配置"
---

# MySQL 配置

主配置文件位于 `config/mysql.jsonc`，负责提供在使用 `MySQL` 时的配置。

| 字段名            | 类型     | 默认值     | 说明      |
|:---------------|:-------|:--------|:--------|
| `disable_pool` | `bool` | `false` | 是否禁用连接池 |
| `pool_size`    | `int`  | `40`    | 连接池大小   |
| `max_overflow` | `int`  | `60`    | 连接池溢出大小 |

!!! warning "除非有特殊需求，否则不建议打开禁用连接池"
