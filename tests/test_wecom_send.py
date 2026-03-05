import pytest
import respx
import httpx
from app.services.wecom_service import wecom_service
from app.core.config import settings


@pytest.mark.asyncio
@respx.mock
async def test_get_access_token():
    # Mocking the access token response
    respx.get(
        f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={settings.WECOM_CORP_ID}&corpsecret={settings.WECOM_CORP_SECRET}").mock(
        return_value=httpx.Response(200, json={"errcode": 0, "access_token": "test_token", "expires_in": 7200})
    )

    token = await wecom_service.get_access_token()
    assert token == "test_token"
    assert wecom_service._access_token == "test_token"


@pytest.mark.asyncio
@respx.mock
async def test_send_text_message():
    # Mocking access token
    wecom_service._access_token = "test_token"
    wecom_service._token_expires_at = 9999999999

    # Mocking the send message response
    respx.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=test_token").mock(
        return_value=httpx.Response(200, json={"errcode": 0, "errmsg": "ok", "msgid": "xxxx"})
    )

    result = await wecom_service.send_text_message("Hello World", touser="UserID")
    assert result["errcode"] == 0
    assert result["msgid"] == "xxxx"


@pytest.mark.asyncio
@respx.mock
async def test_send_text_message_to_party():
    # Mocking access token
    wecom_service._access_token = "test_token"
    wecom_service._token_expires_at = 9999999999

    # Mocking the send message response
    respx.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=test_token").mock(
        return_value=httpx.Response(200, json={"errcode": 0, "errmsg": "ok", "msgid": "party_msg_id"})
    )

    result = await wecom_service.send_text_message("Party Hello", toparty="123|456")
    assert result["errcode"] == 0
    assert result["msgid"] == "party_msg_id"


@pytest.mark.asyncio
@respx.mock
async def test_send_text_message_no_recipient():
    # Mocking access token
    wecom_service._access_token = "test_token"
    wecom_service._token_expires_at = 9999999999

    # Mocking the send message response
    respx.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=test_token").mock(
        return_value=httpx.Response(200, json={"errcode": 0, "errmsg": "ok", "msgid": "no_recipient_msg_id"})
    )

    result = await wecom_service.send_text_message("hello world", touser="@all")
    assert result["errcode"] == 0
