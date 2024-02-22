from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBasicCredentials
import hashlib
# 
from user.models import user as User

async def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


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
    
    
    