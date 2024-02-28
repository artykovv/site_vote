from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from jwt.exceptions import ExpiredSignatureError
from typing import Optional
# 
from database import get_async_session
from user.schemas import CreateUser, TokenInfo, ReadUser
from user.models import user as User
from user.jwt import decode_token
from user.functions import (hash_password, 
                            authenticate, 
                            generate_access_token, 
                            generate_refresh_token,
                            check_permission,
                            get_users,  
                            get_user_by_token,
                            return_user,
                            get_permissions, 
                            get_role_by_id,
                            validate_access_token, validate_refresh_token, 
                            )

security = HTTPBasic()


router = APIRouter(
	# prefix="/api/v1/auth",
	prefix="",
	tags=["User"]
)

# user register
# @router.get("/register")
async def register(
    user_create: CreateUser,
    session: AsyncSession = Depends(get_async_session)

):
    hash_pass = await hash_password(user_create.password)
    user_create.password = hash_pass
    stmt = insert(User).values(**user_create.dict())
    await session.execute(stmt)
    await session.commit()
    return {"detail": "status success"}

# user login and return access&refresh tokens
@router.post("/login")
async def login_user(
    response: Response,
    credentials: HTTPBasicCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session),
):
    user = await authenticate(credentials, session)
    if not user:
        return {"message": "User not found"}
    user = user[0]
    access_token = await generate_access_token(user) 
    refresh_token = await generate_refresh_token(user)
    response.set_cookie(key="access", value=access_token, httponly=True, secure=True, max_age=300)
    response.set_cookie(key="refresh", value=refresh_token, httponly=True, secure=True, max_age=4320)
    return {"message": "Successful login",  "access": access_token, "refresh": refresh_token}


@router.get("/")
async def get(id: int, token: str, response: Response, session: AsyncSession = Depends(get_async_session)):
    has_permission = await check_permission(token, session, response)
    
    if has_permission and "delete" in has_permission:
        if has_permission["delete"]:
            return await get_users(session)
        else:
            return {"У вас нет прав"}
    else:
        return {"Ошибка: недостаточно прав или неверный токен"}