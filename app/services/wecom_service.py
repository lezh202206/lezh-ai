import xml.etree.ElementTree as ET
import httpx
import time
from app.core.wecom_crypto import wxcpt
from app.core.config import settings
from typing import Optional, Dict, Any


class WeComService:
    def __init__(self):
        self._access_token = None
        self._token_expires_at = 0

    async def get_access_token(self) -> str:
        """
        获取企业微信 Access Token
        """
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={settings.WECOM_CORP_ID}&corpsecret={settings.WECOM_CORP_SECRET}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if data.get("errcode") == 0:
                self._access_token = data["access_token"]
                # 提前 5 分钟过期
                self._token_expires_at = time.time() + data["expires_in"] - 300
                return self._access_token
            else:
                raise Exception(f"Get access token failed: {data}")

    async def send_text_message(
            self,
            content: str,
            touser: Optional[str] = "@all",
            toparty: Optional[str] = None,
            totag: Optional[str] = None,
            safe: int = 0,
            enable_id_trans: int = 0,
            enable_duplicate_check: int = 0,
            duplicate_check_interval: int = 1800
    ) -> Dict[str, Any]:
        """
        主动发送文本消息 (企业微信文档: https://developer.work.weixin.qq.com/document/path/90236)
        :param content: 消息内容
        :param touser: 指定接收消息的成员，多个接收者用‘|’分隔，最多支持1000个。指定为"@all"，则向该企业应用的全部成员发送
        :param toparty: 指定接收消息的部门，多个接收者用‘|’分隔，最多支持100个
        :param totag: 指定接收消息的标签，多个接收者用‘|’分隔，最多支持100个
        :param safe: 表示是否是保密消息，0表示可对外分享，1表示不能分享且内容显示水印，默认为0
        :param enable_id_trans: 表示是否开启id转译，0表示否，1表示是，默认为0
        :param enable_duplicate_check: 表示是否开启重复消息检查，0表示否，1表示是，默认为0
        :param duplicate_check_interval: 表示是否重复消息检查的时间间隔，默认1800秒，最大不超过4小时
        """

        token = await self.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"

        payload = {
            "msgtype": "text",
            "agentid": settings.WECOM_AGENT_ID,
            "text": {
                "content": content
            },
            "safe": safe,
            "enable_id_trans": enable_id_trans,
            "enable_duplicate_check": enable_duplicate_check,
            "duplicate_check_interval": duplicate_check_interval
        }

        if touser: payload["touser"] = touser
        if toparty: payload["toparty"] = toparty
        if totag: payload["totag"] = totag

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()
            if data.get("errcode") != 0:
                raise Exception(f"Send message failed: {data}")
            return data

    def handle_received_message(self, msg_signature: str, timestamp: str, nonce: str, body: bytes) -> Dict[str, Any]:
        """
        统一处理接收到的企业微信消息
        :return: 包含消息详情的字典
        """
        # 1. 解密
        sMsg = self.decrypt_message(msg_signature, timestamp, nonce, body)
        
        # 2. 解析 XML
        message_dict = self.parse_xml_to_dict(sMsg)
        
        # 3. 结构化输出，方便 LLM 处理
        # 根据 MsgType 可以做一些基础的字段提取
        msg_type = message_dict.get("MsgType")
        result = {
            "from_user": message_dict.get("FromUserName"),
            "create_time": message_dict.get("CreateTime"),
            "msg_type": msg_type,
            "msg_id": message_dict.get("MsgId"),
            "raw_data": message_dict  # 保留原始数据以备不时之需
        }
        
        if msg_type == "text":
            result["content"] = message_dict.get("Content")
        elif msg_type == "image":
            result["media_id"] = message_dict.get("MediaId")
            result["pic_url"] = message_dict.get("PicUrl")
        elif msg_type == "event":
            result["event"] = message_dict.get("Event")
            result["event_key"] = message_dict.get("EventKey")
            
        return result

    def verify_url(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        """
        验证企业微信回调 URL
        """
        ret, sReplyMsg = wxcpt.verify_url(msg_signature, timestamp, nonce, echostr)
        if ret != 0:
            raise Exception(f"Verify URL failed with error code: {ret}")
        return sReplyMsg

    def decrypt_message(self, msg_signature: str, timestamp: str, nonce: str, body: bytes) -> str:
        """
        解密接收到的消息
        """
        try:
            xml_data = ET.fromstring(body)
            encrypt_msg = xml_data.find("Encrypt").text
        except Exception as e:
            raise Exception("Invalid XML format")

        ret, sMsg = wxcpt.decrypt(encrypt_msg)
        if ret != 0:
            raise Exception(f"Decrypt failed with error code: {ret}")

        return sMsg

    def parse_xml_to_dict(self, xml_str: str) -> Dict[str, Any]:
        """
        将解密后的 XML 转换为字典
        """
        root = ET.fromstring(xml_str)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result


wecom_service = WeComService()
