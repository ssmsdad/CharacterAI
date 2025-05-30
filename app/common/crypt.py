# 2024/4/25
# zhangzhong

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

'''
用户在注册与登陆时，这两个函数的调用流程如下：
1. 注册时，用户输入密码，调用encrypt_password函数加密密码，并存储到数据库中,明文密码从不被存储。
2. 登陆时，用户输入密码，调用verify_password函数验证密码是否正确。
3. 登陆成功后，调用create_access_token函数生成JWT token，并返回给用户。
4. 客户端在后续请求中使用此令牌进行身份验证
'''

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def encrypt_password(password: str) -> str:
    return pwd_context.hash(password)
