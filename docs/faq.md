---
description: "常见问题"
---

# 常见问题

## 发送消息时提示 `graia.ariadne.exception.RemoteException`

该类报错需要读取错误详情

* `MessageSvcPbSendMsg.Response.Failed(resultType=46, ...)`

        账号被冻结群消息发送，可手动登录机器人账号发送群消息解除冻结。

## 启动时提示 `library.model.exception.RequirementResolveFailed`

出现此报错说明你安装的模块依赖了其他未被安装的模块，可通过对比 `metadata.json`
与实际安装的模块列表来解决。

!!! note "一般情况下更加推荐使用内置的模块管理器来安装模块，而不是手动安装。"

      使用内置的模块管理器安装模块时，会自动解决依赖关系。当然你也可以自行通过模块文件夹下的
     `metadata.json` 来查看并解决模块的依赖关系。

## 模块获取了错误的 `channel`

检查该模块是否被其他模块依赖，如果是的话，检查依赖该模块的模块是否被正确安装或 `metadata.json`
是否未填写 `required` 字段。
