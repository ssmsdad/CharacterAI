# 2024/5/9
# zhangzhong
# admin related API

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query
from thefuzz import fuzz, process

from app.common import model
from app.common.minio import minio_service
from app.database import DatabaseService, schema
from app.dependency import get_admin, get_db

admin = APIRouter(prefix="/api/admin")


# db是通过依赖注入而不是头文件引入的原因是：
# 数据库连接需要为每个请求创建一个新的实例，并在请求结束后正确关闭。使用依赖注入可以确保这种生命周期管理自动发生！！（重要，学到了）
@admin.post("/user/update-profile")
async def admin_user_update(
    db: Annotated[DatabaseService, Depends(dependency=get_db)],
    _: Annotated[schema.User, Depends(get_admin)],
    update: model.AdminUpdateUserProfile,
#  FastAPI会自动将数据库模型(schema.User)尝试转换为响应模型(model.UserOut)
) -> model.UserOut:
    update = minio_service.update_avatar_url(obj=update)
    return db.update_user(uid=update.uid, user_update=update)


@admin.post("/user/update-role")
async def update_role(
    db: Annotated[DatabaseService, Depends(dependency=get_db)],
    _: Annotated[schema.User, Depends(get_admin)],
    request: model.UpdateRole,
):
    db.update_user_role(uid=request.uid, role=request.role)


@admin.post("/user/delete")
async def delete_users(
    db: Annotated[DatabaseService, Depends(dependency=get_db)],
    _: Annotated[schema.User, Depends(get_admin)],
    uids: Annotated[list[int], Body(description="uid列表", examples=[[1, 2, 3]])],
) -> None:
    for uid in uids:
        db.delete_user(uid=uid)


@admin.get("/user/select")
async def user_all(
    db: Annotated[DatabaseService, Depends(dependency=get_db)],
    _: Annotated[schema.User, Depends(get_admin)],
    page_num: Annotated[int, Query(description="页码")] = 1,
    page_size: Annotated[int, Query(description="每页数量")] = 10,
    query: str | None = None,
) -> model.UserSelectResponse:
    skip = (page_num - 1) * page_size
    limit = page_size

    # 计算user.name与query的相似度,从0-100
    def sort_by_fuzz(user: schema.User) -> int:
        return fuzz.ratio(user.name, query)
    
    scores = []
    if query is not None:
        users = db.get_users(skip=0, limit=9999999999)
        # 将所有用户的name与query进行模糊匹配，并且降序排序
        users = sorted(users, key=sort_by_fuzz, reverse=True)
        users = users[skip : skip + limit]
        scores = [fuzz.ratio(user.name, query) for user in users]
    else:
        users = db.get_users(skip=skip, limit=limit)

    user_outs: list[model.UserOut] = []
    for user in users:
        # user.__dict__是一个字典，包含了所有的属性和属性值,**表示将字典中的键值对作为关键字参数传递给UserOut类的构造函数
        # 因为user是一个schema.User对象，pydantic对象才有model_dump()方法，所以需要调用__dict()__方法将其转换为字典
        user_out = model.UserOut(**user.__dict__)
        user_outs.append(user_out)

    return model.UserSelectResponse(
        users=user_outs,
        scores=scores,
        total=db.get_user_count(),
    )


@admin.get("/character/select")
async def character_all(
    db: Annotated[DatabaseService, Depends(dependency=get_db)],
    _: Annotated[schema.User, Depends(get_admin)],
    uid: int | None = None,
    query: str | None = None,
    page_num: Annotated[int, Query(description="页码")] = 1,
    page_size: Annotated[int, Query(description="每页数量")] = 10,
) -> model.CharacterSelectResponse:
    skip = (page_num - 1) * page_size
    limit = page_size

    total = 0
    if uid is None:
        total = db.get_character_count()
    else:
        total = db.get_user_character_count(uid=uid)

    characters = db.get_characters(
        where=model.CharacterWhere(uid=uid),
        skip=skip,
        limit=limit,
    )

    def sort_by_fuzz(character: schema.Character) -> int:
        return fuzz.ratio(character.name, query)

    characters = sorted(characters, key=sort_by_fuzz, reverse=True)
    scores = []
    if query is not None:
        scores = [fuzz.ratio(character.name, query) for character in characters]

    character_outs: list[model.CharacterOut] = []
    for character in characters:
        character_out = model.CharacterOut(**character.__dict__)
        character_outs.append(character_out)

    return model.CharacterSelectResponse(
        characters=character_outs,
        scores=scores,
        total=total,
    )
