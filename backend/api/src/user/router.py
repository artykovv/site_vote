from fastapi import APIRouter
from fastapi import Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
import jwt
# 
from database import get_async_session
from user.schemas import CreateUser, TokenInfo
from user.models import user as User
from user.functions import hash_password, authenticate, get_users
from user.jwt import encoded_jwt, decoded_jwt, encoded_jwt_refresh

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
    response.set_cookie(key="token", value=token, httponly=True)
    return {
        "access_token": token,
        "refresh_token": refresh,
        "token_type": "Bearer"
    }
    
@router.get("/users")
async def get(session: AsyncSession = Depends(get_async_session)):
    users = await get_users(session)
    return users