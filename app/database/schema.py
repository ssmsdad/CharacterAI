# 2024/4/7
# zhangzhong
# https://www.sqlalchemy.org/
# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes

from datetime import datetime

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker

from app.common import conf, model


SQLALCHEMY_DATABASE_URL = conf.get_postgres_sqlalchemy_database_url()
# 创建数据库引擎（用于建立与不同数据库的连接），连接池大小为32
engine = create_engine(url=SQLALCHEMY_DATABASE_URL, pool_size=32)
# 创建会话类（用于创建于数据库交互的会话对象），autocommit=False表示不自动提交，autoflush=False表示不自动刷新
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 创建数据库表，建立表之间的关系，创建索引，添加约束等
def init_db():
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = "users"

    # index为True，表示该字段会创建索引，提高查询效率
    uid: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[str] = mapped_column(default=model.Role.USER.value)
    avatar_description: Mapped[str] = mapped_column()
    avatar_url: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime | None] = mapped_column(default=None)
    password: Mapped[str] = mapped_column()
    is_deleted: Mapped[bool] = mapped_column(default=False)

    # relationship用来声明模型之间的关系，这样就可以通过user.characters 获取该用户的所有角色，通过 character.associated_user 获取该角色所属的用户
    characters: Mapped[list["Character"]] = relationship(
        back_populates="associated_user"
    )
    chats: Mapped[list["Chat"]] = relationship(back_populates="associated_user")

    def is_admin(self) -> bool:
        return self.role == model.Role.ADMIN.value


class Character(Base):
    __tablename__ = "characters"

    cid: Mapped[int] = mapped_column(primary_key=True, index=True)
    uid: Mapped[int] = mapped_column(ForeignKey("users.uid"))
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()
    avatar_description: Mapped[str] = mapped_column(default="")
    avatar_url: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)
    is_shared: Mapped[bool] = mapped_column(default=False)
    knowledge_id: Mapped[str] = mapped_column(default="")

    associated_user: Mapped[User] = relationship(back_populates="characters")


class Chat(Base):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uid: Mapped[int] = mapped_column(ForeignKey("users.uid"))
    cid: Mapped[int] = mapped_column(ForeignKey("characters.cid"))
    create_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    associated_user: Mapped[User] = relationship(back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="associated_chat")


class Message(Base):
    __tablename__ = "messages"

    mid: Mapped[int] = mapped_column(primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.chat_id"))
    sender: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    associated_chat: Mapped[Chat] = relationship(back_populates="messages")
