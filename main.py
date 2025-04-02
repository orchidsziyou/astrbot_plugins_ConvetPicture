import os

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import File


@register("Convert", "orchidsziyou", "qq表情转化成可以保存的图片", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @filter.command("转换")
    async def convert_command(self, event: AstrMessageEvent):
        '''这是一个 转换图片格式 指令'''

        message_chain = event.get_messages()

        for msg in message_chain:
            if msg.type == 'Image':
                PictureID = msg.file
                from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
                assert isinstance(event, AiocqhttpMessageEvent)
                client = event.bot
                payloads2 = {
                    "file_id": PictureID
                }
                response = await client.api.call_action('get_image', **payloads2)  # 调用 协议端  API
                # print(response)
                localdiskpath = response['file']

                abs_history_json_path = os.path.abspath(localdiskpath)
                print(abs_history_json_path)
                file_url = f'file://{abs_history_json_path}'

                filename = ""

                if abs_history_json_path.endswith(".jpg"):
                    filename = "图片.jpg"
                if abs_history_json_path.endswith(".png"):
                    filename = "图片.png"
                if abs_history_json_path.endswith(".gif"):
                    filename = "图片.gif"

                chain = [
                    File(file=file_url, name=filename)
                ]

                yield event.chain_result(chain)
            elif msg.type == 'Reply':
                # 处理回复消息
                from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
                assert isinstance(event, AiocqhttpMessageEvent)
                client = event.bot
                payload = {
                    "message_id": msg.id
                }
                response = await client.api.call_action('get_msg', **payload)  # 调用 协议端  API
                reply_msg = response['message']
                for msg in reply_msg:
                    if msg['type'] == 'image':
                        from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import \
                            AiocqhttpMessageEvent
                        assert isinstance(event, AiocqhttpMessageEvent)
                        client = event.bot
                        payloads2 = {
                            "file_id": msg['data']['file']
                        }
                        response = await client.api.call_action('get_image', **payloads2)  # 调用 协议端  API
                        localdiskpath = response['file']

                        abs_history_json_path = os.path.abspath(localdiskpath)
                        print(abs_history_json_path)
                        file_url = f'file://{abs_history_json_path}'

                        filename = ""

                        if abs_history_json_path.endswith(".jpg"):
                            filename = "图片.jpg"
                        if abs_history_json_path.endswith(".png"):
                            filename = "图片.png"
                        if abs_history_json_path.endswith(".gif"):
                            filename = "图片.gif"

                        chain = [
                            File(file=file_url, name=filename)
                        ]

                        yield event.chain_result(chain)

