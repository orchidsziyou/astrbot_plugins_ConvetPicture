# ConvertPicture 插件

## 介绍

由于QQ现在没办法直接保存别人发的gif或者表情，用其他方法也麻烦,本插件就是为了解决这个问题的。

## 依赖
本插件使用了aiochttp的API，**仅在Napcat下测试过**，其他环境可能无法正常运行。
**建议使用了Napcat的用户安装使用本插件**

## 原理
本插件使用了aiochttp的API，通过API将图片转换为其他格式。
实现方法为：
1.从本地文件里面读取图片，获取接收到的图片的路径
2.以 *文件* 的格式发送图片
之后图片即可保存

## 使用
回复某图片，发送 */转换* 即可。之后bot会发送转换后的文件。
如果图片是静态图片，发送后的图片直接保存即可。
如果图片是gif，需要点击 *查看原图* 之后图片才会动。
### 注意：
由于本插件的原理是把图片以文件的形式发送，因此尽量私聊使用，否则会产生很多的群文件，导致群里面有用的群文件被淹没。

## 更新日志
-2025/5/11:
修复了较新版本的astrbot无法正常使用的问题，推测原因是以下代码导致的：
```angular2html
chain = [
    File(file=file_url, name=filename) 
    ] 
yield event.chain_result(chain)
```
修改为了直接调用NapCat的Api来发送文件，具体代码如下：
```angular2html
                from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
                assert isinstance(event, AiocqhttpMessageEvent)
                if event.get_message_type() == MessageType.FRIEND_MESSAGE:
                    user_id = event.get_sender_id()
                    client = event.bot
                    payloads2 = {
                        "user_id": user_id,
                        "message": [
                            {
                                "type": "file",
                                "data": {
                                    "file": file_url,
                                    "name": filename
                                }
                            }
                        ]
                    }
                    await client.api.call_action('send_private_msg', **payloads2)  # 调用 协议端  API
                if event.get_message_type() == MessageType.GROUP_MESSAGE:
                    group_id = event.get_group_id()
                    client = event.bot
                    payloads2 = {
                        "group_id": group_id,
                        "message": [
                            {
                                "type": "file",
                                "data": {
                                    "file": file_url,
                                    "name": filename
                                }
                            }
                        ]
                    }
                    await client.api.call_action('send_group_msg', **payloads2)  # 调用 协议端
```


