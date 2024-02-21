from fastapi import APIRouter
from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
# 
from database import get_async_session
from user.schemas import CreateUser, TokenInfo
from user.models import user as User
from user.functions import hash_password, authenticate
from user.jwt import encoded_jwt, decoded_jwt

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
    token = encoded_jwt(user_data)
    response.set_cookie(key="token", value=token, httponly=True)
    return {
        "access_token": token,
        "token_type": "Bearer"
    }
    

@router.get("/get")
async def get(session: AsyncSession = Depends(get_async_session)):
    query = select(User)
    result = await session.execute(query)
    return result.mappings().all()
