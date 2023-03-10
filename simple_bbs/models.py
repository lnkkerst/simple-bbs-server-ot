import time
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    password_salt = Column(String)
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    content = Column(String)
    author_id = Column(String, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    publish_at = Column(Integer, default=lambda: int(time.time()))


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(String)
    author_id = Column(String, ForeignKey("users.id"))
    post_id = Column(String, ForeignKey("posts.id"))
    author = relationship("User", back_populates="comments")
    publish_at = Column(Integer, default=lambda: int(time.time()))
