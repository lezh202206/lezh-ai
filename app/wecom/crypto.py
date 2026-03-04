import base64
import hashlib
import struct
import socket
import time
import xml.etree.ElementTree as ET
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class WXBizMsgCrypt:
    def __init__(self, sToken, sEncodingAESKey, sReceiveId):
        self.sToken = sToken
        self.sEncodingAESKey = sEncodingAESKey
        self.sReceiveId = sReceiveId
        self.key = base64.b64decode(sEncodingAESKey + "=")
        assert len(self.key) == 32

    def get_signature(self, sToken, sTimeStamp, sNonce, sEncryptMsg):
        """生成签名"""
        try:
            sort_list = [sToken, sTimeStamp, sNonce, sEncryptMsg]
            sort_list.sort()
            sha = hashlib.sha1()
            sha.update("".join(sort_list).encode('utf-8'))
            return sha.hexdigest()
        except Exception as e:
            return None

    def verify_url(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        """验证URL有效性"""
        signature = self.get_signature(self.sToken, sTimeStamp, sNonce, sEchoStr)
        if signature != sMsgSignature:
            return -40001, None
        
        ret, sReplyMsg = self.decrypt(sEchoStr)
        return ret, sReplyMsg

    def decrypt(self, sPostData):
        """解密消息"""
        try:
            aes_msg = base64.b64decode(sPostData)
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.key[:16]), backend=default_backend())
            decryptor = cipher.decryptor()
            plain_text = decryptor.update(aes_msg) + decryptor.finalize()
        except Exception as e:
            return -40004, None

        try:
            # 去除 PKCS7 填充
            pad = plain_text[-1]
            if pad < 1 or pad > 32:
                pad = 0
            plain_text = plain_text[:-pad]
            
            # 分离内容
            content = plain_text[16:]
            xml_len = struct.unpack(">I", content[:4])[0]
            xml_content = content[4:xml_len + 4].decode('utf-8')
            from_receiveid = content[xml_len + 4:].decode('utf-8')
        except Exception as e:
            return -40005, None

        if from_receiveid != self.sReceiveId:
            return -40005, None
        
        return 0, xml_content

    def encrypt(self, sReplyMsg, sNonce):
        """加密消息"""
        try:
            # 拼接 16字节随机串 + 4字节内容长度 + 内容 + receiveid
            random_str = b"a" * 16 # 这里可以用真正的随机串，但验证阶段通常固定或不要求
            text = sReplyMsg.encode('utf-8')
            text_len = struct.pack(">I", len(text))
            receiveid = self.sReceiveId.encode('utf-8')
            
            full_content = random_str + text_len + text + receiveid
            
            # PKCS7 填充
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(full_content) + padder.finalize()
            
            # AES 加密
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.key[:16]), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            sEncryptMsg = base64.b64encode(encrypted_data).decode('utf-8')
            sTimeStamp = str(int(time.time()))
            sMsgSignature = self.get_signature(self.sToken, sTimeStamp, sNonce, sEncryptMsg)
            
            return 0, (sEncryptMsg, sMsgSignature, sTimeStamp)
        except Exception as e:
            return -40006, None
