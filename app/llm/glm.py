# 2024/2/6
# zhangzhong

import requests

from app.common import conf
from app.common.model import RequestPayload, ResponseModel

def character_llm(payload: RequestPayload) -> ResponseModel:
    response = requests.post(
        conf.get_glm2_url(),
        json=payload.model_dump(),
    )
    # eval将字符串转换为Python对象（dict）
    response_dict = eval(response.json()["message"])
    return ResponseModel(message=response_dict["response"])

