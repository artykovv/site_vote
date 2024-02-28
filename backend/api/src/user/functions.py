import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBasicCredentials
from jwt.exceptions import ExpiredSignatureError
import hashlib
from fastapi import Response
from typing import Callable, Union, List
from user.models import user as User, role as Role
from user.jwt import encoded_jwt, encoded_jwt_refresh, decode_token


# hash password
async def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# login and validate username & password
async def authenticate(credentials: HTTPBasicCredentials, session: AsyncSession):
    hashed_password = await hash_password(credentials.password)
    query = select(User).where(
        User.c.username == credentials.username,
        User.c.password == hashed_password
    )
    result = await session.execute(query)
    return result.mappings().all()

async def get_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    user_data_list = []
    for row in result.mappings().all():
        user_data = {
            'id': row.id,
            'username': row.username,
            'email': row.email,
            'is_active': row.is_active,
            'role_id': row.role_id
        }
        user_data_list.append(user_data)
    return user_data_list

# access
async def generate_access_token(user):
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'role_id': user.role_id
    }
    return encoded_jwt(user_data)

# refresh
async def generate_refresh_token(user):
    user_data = {
        'username': user.username,
    }
    return encoded_jwt_refresh(user_data)

# def return
async def return_user(user):
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'role_id': user.role_id
    }
    return user_data

# refresh
async def validate_refresh_token(token: str, session: AsyncSession, response: Response,):
    token_decode = decode_token(token)
    query = select(User).where(User.c.username == token_decode["username"])
    result = await session.execute(query)
    user = result.mappings().all()
    user = user[0]
    access_token = await generate_access_token(user)
    response.set_cookie(key="access", value=access_token, httponly=True, secure=True, max_age=300)
    return user

# access
async def validate_access_token(token: str, session: AsyncSession): 
    token_decode = decode_token(token)
    query = select(User).where(
        User.c.id == token_decode["id"],
        User.c.username == token_decode["username"],
        User.c.email == token_decode["email"],
        User.c.is_active == token_decode["is_active"],
        User.c.role_id == token_decode["role_id"],
        )
    result = await session.execute(query)
    return result.mappings().all()

# Функция для получения роли пользователя по его ID из базы данных
async def get_role_by_id(role_id: int, session: AsyncSession):
    query = select(Role).where(Role.c.id == role_id)
    result = await session.execute(query)
    return result.mappings().all()

# Функция для получения разрешений пользователя
async def get_permissions(user, session):
    role = await get_role_by_id(user.role_id, session)
    role = role[0]
    return role

# 
async def check_permission(token: str, session: AsyncSession, response: Response,):
    token_decode = decode_token(token)
    if all(key in token_decode for key in ["id", "username", "email", "is_active", "role_id"]):
        valid = await validate_access_token(token, session)
        user = valid[0]
        permission = await get_permissions(user, session)
        permissions = permission.get("permissions", {})
        return permissions
    elif "username" in token_decode and "exp" in token_decode:
        valid = await validate_refresh_token(token, session, response)
        user = valid
        permission = await get_permissions(user, session)
        permissions = permission.get("permissions", {})
        access_token = await generate_access_token(user)
        response.set_cookie(key="access", value=access_token, httponly=True, secure=True, max_age=300)
        return permissions
    else: 
        return False


async def get_user_by_token(token: str, session: AsyncSession):
    token_decode = decode_token(token)
    username = token_decode["username"]
    query = select(User).where(User.c.username == username)
    result = await session.execute(query)
    return result.mappings().all()





