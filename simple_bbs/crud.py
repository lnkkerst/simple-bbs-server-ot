from sqlalchemy.orm import Session
import random

from simple_bbs.utils import hash_password

from . import models, schemas


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    salt = str(random.randint(1, 1000000000))
    hashed_password = hash_password(user.password, salt)
    db_user = models.User(
        username=user.username, password_hash=hashed_password, password_salt=salt
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    else:
        return None


def get_post(db: Session, post_id: str):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def get_posts_by_title(db: Session, post_title: str):
    return db.query(models.Post).filter(models.Post.title == post_title).all()


def get_posts_by_author(
    db: Session, post_author_id: str, skip: int = 0, limit: int = 0
):
    return (
        db.query(models.Post)
        .filter(models.Post.author_id == post_author_id)
        .order_by(-models.Post.publish_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_posts(db: Session, author_id=None, skip: int = 0, limit: int = 20):
    query = db.query(models.Post)
    if author_id:
        query = query.filter(models.Post.author_id == author_id)
    return query.order_by(-models.Post.publish_at).offset(skip).limit(limit).all()


def create_post(db: Session, user_id: str, post: schemas.PostCreate):
    db_post = models.Post(**post.dict(), author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_comment(db: Session, comment_id: str):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def get_comments(
    db: Session, author_id=None, post_id=None, skip: int = 0, limit: int = 20
):
    query = db.query(models.Comment)
    if author_id:
        query = query.filter(models.Comment.author_id == author_id)
    if post_id:
        query = query.filter(models.Comment.post_id == post_id)
    return query.order_by(-models.Comment.publish_at).offset(skip).limit(limit).all()


def get_comments_by_post_id(db: Session, post_id: str, skip: int = 0, limit: int = 20):
    return (
        db.query(models.Comment)
        .filter(models.Comment.post_id == post_id)
        .order_by(-models.Comment.publish_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_comments_by_author_id(
    db: Session, author_id: str, skip: int = 0, limit: int = 20
):
    return (
        db.query(models.Comment)
        .filter(models.Comment.author_id == author_id)
        .order_by(-models.Comment.publish_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_comment(db: Session, user_id: str, comment: schemas.CommentCreate):
    db_comment = models.Comment(**comment.dict(), author_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
