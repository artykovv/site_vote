from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
# 
from database import get_async_session
from user.models import user as User, role as Role
from user.functions import get_users, validate_token, permission_check, return_user, validate_refresh_token


router = APIRouter(
	prefix="/api/v1/admin",
	tags=["Admin"]
)

# get all users 
@router.get("/users")
async def get_all_users(
    token: str,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
    ):
    user = await validate_token(token, session, response)
    permissions = await permission_check(user, session)
    
    if all(permissions[key] for key in ["read", "write"]):
        query = select(
            User.c.id,
            User.c.username,
            User.c.email,
            User.c.is_active,
            User.c.registered_at,
            Role.c.permissions
        ).select_from(
            User.join(Role, User.c.role_id == Role.c.id)
        )
        result = await session.execute(query)
        users = result.mappings().all()
        return users
    else:
        return False

# get user by id
@router.get("/user/{id}")
async def get_user_by_id(
    token: str,
    id: int,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
):
    users = await validate_token(token, session, response)
    permissions = await permission_check(users, session)
    
    if all(permissions[key] for key in ["read", "write"]):
        query = select(User).where(User.c.id == id)
        result = await session.execute(query)
        user = result.mappings().all()
        user = user[0]
        user = await return_user(user)
        return user
    else:
        False

# delete user by id
@router.delete("/user/{id}")
async def delete_user_by_id(
    token: str,
    id: int,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
):
    users = await validate_token(token, session, response)
    permissions = await permission_check(users, session)
    if all(permissions[key] for key in ["read", "write", "delete"]):
        query = delete(User).where(User.c.id == id)
        await session.execute(query)
        await session.commit()
        return {"deleted": id}
    else:
        return False

# 
@router.put("/users/{id}/activate")
async def active_user_by_id(
    token: str,
    id: int,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
):
    users = await validate_token(token, session, response)
    permissions = await permission_check(users, session)
    if all(permissions[key] for key in ["read", "write"]):
        stmt = update(User).where(User.c.id == id).values(is_active = True)
        await session.execute(stmt)
        await session.commit()
        return {"active": id}
    else:
        return False

# put request deactive user
@router.put("/users/{id}/deactivate")
async def deactivate_uesr_by_id(
    token: str,
    id: int,
    response: Response,
    session: AsyncSession = Depends(get_async_session)
):
    users = await validate_token(token, session, response)
    permissions = await permission_check(users, session)
    if all(permissions[key] for key in ["read", "write"]):
        stmt = update(User).where(User.c.id == id).values(is_active = False)
        await session.execute(stmt)
        await session.commit()
        return {"deactivate": id}
    else:
        return False    

# get logs
@router.get("/logs")
def get_logs():
    return