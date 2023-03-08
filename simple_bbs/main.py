from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.responses import JSONResponse

from simple_bbs.utils import hash_password
from .database import SessionLocal, engine
from . import models, crud, schemas

# 自动建立表格
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_access_token_expires: int = 60 * 60 * 24 * 15


@AuthJWT.load_config  # type: ignore
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})  # type: ignore


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login", response_model=schemas.LoginInfo)
def user_login(
    user: schemas.UserLogin,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    """
    ## 登录

    ### Request body:

        username: 用户名
        password: 密码明文

    ### Returns:

        用户信息
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if hash_password(user.password, db_user.password_salt) != db_user.password_hash:  # type: ignore
        raise HTTPException(status_code=400, detail="Password or username incorrect")

    access_token = Authorize.create_access_token(subject=db_user.id)  # type: ignore
    refresh_token = Authorize.create_refresh_token(subject=db_user.id)  # type: ignore
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": db_user.username,
        "userId": db_user.id,
    }


@app.post("/refresh")
def refresh(Authorize: AuthJWT = Depends()):
    """
    ## 刷新 JWT token [TODO]

    - 需要登录

    ### Request body:

        refresh_token: jwt refresh token
    """
    Authorize.jwt_refresh_token_required()

    user_id = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=user_id)  # type: ignore
    return {"access_token": new_access_token}


@app.get("/user", response_model=schemas.User)
def get_current_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    ## 获取当前用户的信息

    - 需要登录

    ### Returns

    - 当前用户信息
    """
    Authorize.jwt_required()
    db_user = crud.get_user(db=db, user_id=Authorize.get_jwt_subject())  # type: ignore
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    ## 注册用户

    ### Request body:

        username: 用户名
        password: 密码明文

    ### Returns:

    - 注册用户的信息
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.delete("/user", response_model=schemas.User)
def delete_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    """
    ## 注销当前账户

    - 需要登录

    """
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    db_user = crud.delete_user(db, user_id=user_id)  # type: ignore
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/posts", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    """
    ## 创建帖子

    - 需要登录

    """
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    return crud.create_post(db=db, post=post, user_id=user_id)  # type: ignore


@app.get("/posts", response_model=list[schemas.Post])
def get_posts(
    author_id=None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """
    ## 获取帖子
    """
    posts = crud.get_posts(db=db, author_id=author_id, skip=skip, limit=limit)
    return posts


@app.get("/users/{user_id}/posts", response_model=list[schemas.Post])
def get_posts_by_author_id(
    user_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """
    ## 获取指定用户的帖子(deprecated)
    """
    return crud.get_posts_by_author(
        db=db, post_author_id=user_id, skip=skip, limit=limit
    )


@app.get("/posts/{post_id}", response_model=schemas.Post)
def get_post_by_id(post_id: str, db: Session = Depends(get_db)):
    """
    ## 获取单条帖子
    """
    return crud.get_post(db=db, post_id=post_id)


@app.post("/comments", response_model=schemas.Comment)
def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    """
    ## 创建评论

    - 需要登录
    """
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    return crud.create_comment(db=db, user_id=user_id, comment=comment)  # type: ignore


@app.get("/comments", response_model=list[schemas.Comment])
def get_comments(
    author_id=None,
    post_id=None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    ## 获取评论
    """
    return crud.get_comments(
        db=db, author_id=author_id, post_id=post_id, skip=skip, limit=limit
    )


@app.get("/comments/{comment_id}", response_model=schemas.Comment)
def get_comment_by_id(comment_id: str, db: Session = Depends(get_db)):
    """
    ## 获取单条评论
    """
    return crud.get_comment(comment_id=comment_id, db=db)


@app.get("/posts/{post_id}/comments", response_model=list[schemas.Comment])
def get_comments_by_post_id(
    post_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """
    ## 获取某个帖子下评论(deprecated)
    """
    return crud.get_comments_by_post_id(db=db, post_id=post_id, skip=skip, limit=limit)


@app.get("/users/{user_id}/comments", response_model=list[schemas.Comment])
def get_comments_by_author_id(
    user_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """
    ## 获取指定用户的所有评论
    """
    return crud.get_comments_by_author_id(
        db=db, author_id=user_id, skip=skip, limit=limit
    )
