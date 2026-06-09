import datetime
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    BOOLEAN,
)

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(100), nullable=False)
    nickname = Column(String(20), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String, nullable=False)
    photo = Column(String(255))
    description = Column(Text)
    is_verified = Column(BOOLEAN, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))


class Board(Base):
    __tablename__ = "board"

    board_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    color = Column(Text, default="F5EEDF")
    user_id = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))


class BoardMembers(Base):
    __tablename__ = "board_with_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    board_id = Column(Integer, ForeignKey("board.board_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    role = Column(
        Enum("owner", "member", name="role_types"), nullable=False, default="member"
    )


class Columns(Base):
    __tablename__ = "columns"

    column_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=True)
    board_id = Column(Integer, ForeignKey("board.board_id"))
    position = Column(Integer)


class Cards(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=True)
    color = Column(Text, default="F7F2FC")
    tast_description = Column(Text)
    column_id = Column(Integer, ForeignKey("columns.column_id"))
    position = Column(Integer)
    priority = Column(Integer)
    tags = Column(Text)
    deadline = Column(DateTime)
    is_template = Column(BOOLEAN, default=False)


class CardMembers(Base):
    __tablename__ = "card_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    card_id = Column(Integer, ForeignKey("cards.id"))
    role = Column(
        Enum("executors", "customer", name="role"),
        nullable=False,
        default="customer",
    )


class Comments(Base):
    __tablename__ = "card_comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    card_id = Column(Integer, ForeignKey("cards.id"))
    content = Column(Text)
    created_at = Column(DateTime, nullable=False)


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    board_id = Column(Integer, ForeignKey("board.board_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    content = Column(Text)
    is_ai = Column(BOOLEAN)
    created_at = Column(DateTime, nullable=False)
