# 2024/2/6
# zhangzhong


from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.common import model
from app.database import DatabaseService, schema


def get_db() -> DatabaseService:
    return DatabaseService()


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# oauth2_scheme是一种从 HTTP 请求中提取 token 的工具
# tokenUrl="/api/user/login"只是告诉在 Swagger UI（API 文档界面）中配置"Authorize"按钮，告诉API文档工具，客户端应该向哪个URL发送认证请求，与代码无关，删了也不影响功能
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


def parse_token(token: str) -> model.TokenData:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    uid: str | None = payload.get("sub")
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return model.TokenData(uid=int(uid))

# 想要获取token的数据首先要确保有tokens，所以要依赖oauth2_scheme
async def get_token_data(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> model.TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: str | None = payload.get("sub")
        if uid is None:
            raise credentials_exception
        token_data = model.TokenData(uid=int(uid))
    except JWTError:
        raise credentials_exception
    return token_data


# 当已经经过密码验证的用户请求时，直接从token中获取用户信息
def get_user(
    token_data: Annotated[model.TokenData, Depends(get_token_data)],
    db: Annotated[DatabaseService, Depends(get_db)],
) -> schema.User:
    user = db.get_user(uid=token_data.uid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_admin(
    user: Annotated[schema.User, Depends(get_user)],
) -> schema.User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permission denied",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
