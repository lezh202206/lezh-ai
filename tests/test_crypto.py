import sys
import os
# 添加当前目录到 sys.path 以便导入 app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.wecom.crypto import WXBizMsgCrypt

def test_crypto():
    # 模拟配置
    token = "test_token"
    aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG" # 43位
    corp_id = "test_corp_id"
    
    wxcpt = WXBizMsgCrypt(token, aes_key, corp_id)
    
    # 1. 测试签名生成
    msg = "test_message"
    timestamp = "12345678"
    nonce = "test_nonce"
    sig = wxcpt.get_signature(token, timestamp, nonce, msg)
    assert sig is not None
    print(f"Signature: {sig}")

    # 2. 测试加密与解密
    test_xml = "<xml><ToUserName>toUser</ToUserName><Content>Hello</Content></xml>"
    ret, encrypt_res = wxcpt.encrypt(test_xml, nonce)
    assert ret == 0
    sEncryptMsg, sMsgSignature, sTimeStamp = encrypt_res
    print(f"Encrypted message: {sEncryptMsg}")

    ret, decrypt_xml = wxcpt.decrypt(sEncryptMsg)
    assert ret == 0
    print(f"Decrypted XML: {decrypt_xml}")
    assert decrypt_xml == test_xml
    
    # 3. 测试验证URL逻辑
    # 验证URL时，企业微信会发 GET 请求，其中 echostr 是加密的字符串
    # 这里的验证逻辑本质上是解密 echostr
    ret, verify_res = wxcpt.verify_url(sMsgSignature, sTimeStamp, nonce, sEncryptMsg)
    assert ret == 0
    assert verify_res == test_xml
    
    print("All crypto tests passed!")

if __name__ == "__main__":
    test_crypto()
