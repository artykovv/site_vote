from fastapi import APIRouter
from fastapi import Depends, Response, Request, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi.responses import JSONResponse
# 
from database import get_async_session
from user.schemas import CreateUser, TokenInfo
from user.models import user as User
from user.functions import hash_password, authenticate, get_users
from user.jwt import encoded_jwt, encoded_jwt_refresh, decode_token

security = HTTPBasic()


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["User"]
)

# user register
@router.post("/register")
async def register_user(
    user_create: CreateUser, 
    session: AsyncSession = Depends(get_async_session)
    ):
    
    hash_pass = await hash_password(user_create.password)
    user_create.password = hash_pass
    
    stmt = insert(User).values(**user_create.dict())
    await session.execute(stmt)
    await session.commit()
    return {"detail": "status success"}


# user login + token
@router.get("/login", response_model=TokenInfo)
async def login_user(
    response: Response,
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session),
):
    user = await authenticate(credentials, session)
    user = user[0]
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'role_id': user.role_id
        }
    re_token = {'username': user.username}
    token = encoded_jwt(user_data)
    refresh = encoded_jwt_refresh(re_token)
    response.set_cookie(key="token", value=token, httponly=False)
    response.set_cookie(key="refresh", value=refresh, httponly=True)
    return {
        "access_token": token,
        "refresh_token": refresh,
        "token_type": "Bearer"
    }
    
@router.get("/get")
async def get_tokens(
    token: str, 
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    ):
    token_decode = decode_token(token)
    username = token_decode["username"]
    query = select(User).where(User.c.username == username)
    result = await session.execute(query)
    user = result.mappings().all()
    user = user[0]
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'role_id': user.role_id
        }
    access_token = encoded_jwt(user_data)
    if user.role_id == 2:
        users = await get_users(session)
        response.set_cookie(key="token", value=access_token, httponly=False)
        return users
    else:
        response.set_cookie(key="token", value=access_token, httponly=False)
        return {"data": "permissions none"}