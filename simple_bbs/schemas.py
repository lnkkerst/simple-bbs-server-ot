from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase):

    """
    ## 用户信息

    ### 字段：

        id: 用户 ID
        username: 用户名
    """

    id: str

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    """
    ## 单条帖子

    ### 字段：

        title: 帖子的标题
        content: 帖子的内容
    """

    pass


class Post(PostBase):
    id: str
    author_id: str
    author: User

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):

    """
    ## 创建评论需要的信息

    ### 字段：

        post_id: 所属帖子的 ID
        content: 评论的内容
    """

    post_id: str


class Comment(CommentBase):
    """
    ## 单条评论

    ### 字段：

        id: 评论的 ID
        author_id: 评论作者的 ID
        author: 评论作者信息
        post_id: 所属帖子 ID
    """

    id: str
    author_id: str
    author: User
    post_id: str

    class Config:
        orm_mode = True


class LoginInfo(BaseModel):
    """
    ## 登陆返回信息

    ### 字段：

        username: 用户名
        userId: 用户 ID
        access_token: jwt access token
        refresh_token: jwt refresh token
    """

    username: str
    userId: str
    access_token: str
    refresh_token: str
