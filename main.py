import json
import os
from typing import List, Union

import aiohttp

from astrbot import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import Image
from astrbot.core.platform import MessageType
from astrbot.core.provider.entities import ProviderRequest, LLMResponse
from astrbot.core.star.filter.permission import PermissionType

global block_grouplist
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


blocklist_path = "./data/plugins/astrbot_plugins_ConvetPicture/blocklist.json"


def _ensure_blocklist_file(blocklist_path: str) -> None:
    """
    确保黑名单文件存在，如果不存在则创建

    Args:
        blocklist_path: 黑名单文件路径
    """
    # 如果目录不存在，创建目录
    directory = os.path.dirname(blocklist_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # 如果文件不存在，创建带有空group_id列表的文件
    if not os.path.exists(blocklist_path):
        with open(blocklist_path, 'w', encoding='utf-8') as f:
            json.dump({"group_id": []}, f, ensure_ascii=False, indent=2)


def get_blocked_groups(blocklist_path: str) -> List[str]:
    """
    读取黑名单中的群组ID列表

    Args:
        blocklist_path: 黑名单文件路径

    Returns:
        List[str]: 群组ID列表
    """
    _ensure_blocklist_file(blocklist_path)

    try:
        with open(blocklist_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("group_id", [])
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件读取失败，重新创建文件并返回空列表
        _ensure_blocklist_file(blocklist_path)
        return []


def add_blocked_group(blocklist_path: str, group_id: Union[str, int]) -> bool:
    """
    添加群组ID到黑名单

    Args:
        blocklist_path: 黑名单文件路径
        group_id: 要添加的群组ID

    Returns:
        bool: 添加成功返回True，如果已存在返回False
    """
    group_id = str(group_id)
    group_ids = get_blocked_groups(blocklist_path)

    # 如果群组ID已存在，不重复添加
    if group_id in group_ids:
        return False

    group_ids.append(group_id)
    _save_group_ids(blocklist_path, group_ids)
    return True


def remove_blocked_group(blocklist_path: str, group_id: Union[str, int]) -> bool:
    """
    从黑名单中移除群组ID

    Args:
        blocklist_path: 黑名单文件路径
        group_id: 要移除的群组ID

    Returns:
        bool: 移除成功返回True，如果不存在返回False
    """
    group_id = str(group_id)
    group_ids = get_blocked_groups(blocklist_path)

    # 如果群组ID不存在，返回False
    if group_id not in group_ids:
        return False

    group_ids.remove(group_id)
    _save_group_ids(blocklist_path, group_ids)
    return True


def _save_group_ids(blocklist_path: str, group_ids: List[str]) -> None:
    """
    保存群组ID列表到文件

    Args:
        blocklist_path: 黑名单文件路径
        group_ids: 群组ID列表
    """
    _ensure_blocklist_file(blocklist_path)
    data = {"group_id": group_ids}
    with open(blocklist_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@register("Convert", "orchidsziyou", "qq表情转化成可以保存的图片", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        global block_grouplist
        block_grouplist = get_blocked_groups(blocklist_path)

    
    @filter.command("转换")
    async def convert_command(self, event: AstrMessageEvent):
        '''这是一个 转换图片格式 指令'''
        event.should_call_llm(False)
        message_chain = event.get_messages()
        # logger.info(message_chain)
        # print(message_chain)

        # 判断群组是否在黑名单中
        if event.get_message_type() == MessageType.GROUP_MESSAGE:
            if event.get_group_id() in block_grouplist:
                yield event.plain_result("该群聊已禁止使用该功能，请私聊使用")
                return

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


    # @filter.on_llm_request()
    # async def on_llm_request(self, event: AstrMessageEvent, req: ProviderRequest):
    #     '''处理来自 LLM 的请求'''
    #     event.stop_event()
    #     return None
    #
    # @filter.on_llm_response()
    # async def on_llm_response(self, event: AstrMessageEvent, resp: LLMResponse):
    #     '''处理来自 LLM 的响应'''
    #     event.stop_event()
    #     return None


    @filter.command_group("convert")
    async def convert_command_group(self, event: AstrMessageEvent):
        ...

    @filter.permission_type(PermissionType.ADMIN)
    @convert_command_group.command("addblock")
    async def addblock(self, event: AstrMessageEvent):
        global block_grouplist
        '''该群添加到blocklist当中'''
        if event.get_message_type() == MessageType.FRIEND_MESSAGE:
            yield event.plain_result("请使用群组进行添加")
            return
        if event.get_message_type() == MessageType.GROUP_MESSAGE:
            group_id = event.get_group_id()
            if group_id in block_grouplist:
                yield event.plain_result("该群组已添加")
                return
            else:
                block_grouplist.append(group_id)
                add_blocked_group(blocklist_path,group_id)
                yield event.plain_result("添加成功")
                return

    @filter.permission_type(PermissionType.ADMIN)
    @convert_command_group.command("delblock")
    async def delblock(self, event: AstrMessageEvent):
        global block_grouplist
        '''该群从blocklist当中删除'''
        if event.get_message_type() == MessageType.FRIEND_MESSAGE:
            yield event.plain_result("请使用群组进行删除")
            return
        if event.get_message_type() == MessageType.GROUP_MESSAGE:
            group_id = event.get_group_id()
            if group_id in block_grouplist:
                block_grouplist.remove(group_id)
                remove_blocked_group(blocklist_path,group_id)
                yield event.plain_result("删除成功")
                return
            else:
                yield event.plain_result("该群组未添加")
                return


