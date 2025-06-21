import os

import aiohttp

from astrbot import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import Image
from astrbot.core.platform import MessageType
from astrbot.core.provider.entities import ProviderRequest, LLMResponse


async def download_image(picture_url, relative_path):
    # 使用 aiohttp 进行异步请求
    async with aiohttp.ClientSession() as session:
        async with session.get(picture_url) as response:
            if response.status == 200:

                content = await response.read()
                # 保存图片到本地
                with open(relative_path, 'wb') as f:
                    f.write(content)
                return True
            else:
                return False


@register("Convert", "orchidsziyou", "qq表情转化成可以保存的图片", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @filter.command("转换")
    async def convert_command(self, event: AstrMessageEvent):
        '''这是一个 转换图片格式 指令'''
        event.should_call_llm(False)
        message_chain = event.get_messages()
        # logger.info(message_chain)
        # print(message_chain)
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
                    event.stop_event()
                    return
            elif msg.type == 'Reply':
                # print(msg)
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
                    # print(msg)
                    if msg['type'] == 'image':
                        # 官方表情没办法保存
                        picture_url = msg['data']['url']
                        print(picture_url)
                        relative_path = './data/plugins/astrbot_plugins_ConvetPicture/downloaded_image.jpg'
                        if "/club/item/" in picture_url:
                            result = await download_image(picture_url,relative_path)
                            if result:
                                current_directory = os.getcwd()
                                absolute_path = os.path.join(current_directory, relative_path)

                                file_url = f'file://{absolute_path}'

                                from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import \
                                    AiocqhttpMessageEvent
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
                                                    "name": "图片.jpg"
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
                                                    "name": "图片.jpg"
                                                }
                                            }
                                        ]
                                    }
                                    await client.api.call_action('send_group_msg', **payloads2)  # 调用 协议端

                                # chain = [
                                #     Image.fromFileSystem('./data/plugins/astrbot_plugins_ConvetPicture/downloaded_image.jpg')
                                # ]
                                # yield event.chain_result(chain)
                            else:
                                yield event.plain_result("图片下载失败")
                            event.stop_event()
                            return
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

                        from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import \
                            AiocqhttpMessageEvent
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
                            event.stop_event()
                            return


    @filter.on_llm_request()
    async def on_llm_request(self, event: AstrMessageEvent, req: ProviderRequest):
        '''处理来自 LLM 的请求'''
        event.stop_event()
        return None

    @filter.on_llm_response()
    async def on_llm_response(self, event: AstrMessageEvent, resp: LLMResponse):
        '''处理来自 LLM 的响应'''
        event.stop_event()
        return None
