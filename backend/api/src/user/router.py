from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# 
from database import get_async_session
from user.schemas import CreateUser, TokenInfo, ReadUser
from user.models import user as User
from user.jwt import decode_token
from user.functions import (hash_password, 
                            authenticate, 
                            generate_access_token, 
                            generate_refresh_token,
                            get_users,
                            validate_token,
                            return_user, permission_check, generate_tokens, user_data_get
                            )

security = HTTPBasic()


router = APIRouter(
	prefix="/api/v1/auth",
	tags=["User"]
)

# user register
@router.get("/register")
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
    user_token = await generate_tokens(user, response) 
    return {"message": "Successful login"}

# update user data username & email
@router.put("/update/my-account")
async def update_user_data(token: str, user_data: ReadUser, response: Response, session: AsyncSession = Depends(get_async_session)):
    user = await validate_token(token, session, response)
    permissions = await permission_check(user, session)
    
    if permissions.get("read"):
        stmt = update(User).where(User.c.id == user.get("id")).values(username=user_data.username, email=user_data.email)
        await session.execute(stmt)
        await session.commit()
        
        data = user.get("id")
        user = await user_data_get(data, session)
        user_token = await generate_tokens(user, response) 
        user = await return_user(user)
        return user
    
    else:
        return {"message": "Insufficient permissions"}
    

