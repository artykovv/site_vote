from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# 
from database import get_async_session
from user.schemas import CreateUser, TokenInfo, ReadUser, EditPassword
from user.models import user as User, role
from user.functions import (hash_password, 
                            authenticate, 
                            validate_token,
                            return_user, permission_check, generate_tokens, user_data_get
                            )

security = HTTPBasic()


router = APIRouter(
	prefix="/api/v1/auth",
	tags=["User"]
)

# user register
@router.post("/register")
async def register(
    user_create: CreateUser,
    session: AsyncSession = Depends(get_async_session)

):
    hash_pass = await hash_password(user_create.password)
    user_create.password = hash_pass
    stmt = insert(User).values(user_create.dict())
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
async def update_user_data(
    token: str, 
    user_data: ReadUser, 
    response: Response, 
    session: AsyncSession = Depends(get_async_session)
    ):
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

@router.patch("/update/password/")
async def update_password(
    token: str, 
    response: Response,
    password: EditPassword,
    session: AsyncSession = Depends(get_async_session)
):
    user = await validate_token(token, session, response)
    validate_pass = await hash_password(password.old_password)
    query = select(User).where(
        User.c.username == user.username,
        User.c.password == validate_pass
    )
    new_pass = await hash_password(password.new_password)
    stmt = update(User).where(User.c.id == user.get("id")).values(password=new_pass)
    await session.execute(stmt)
    await session.commit()
    return {"data": "success"}

@router.post("/verify-email")
def verify_email():
    return

@router.get("/confirm-email")
def confirm_email():
    return

# для запроса на сброс пароля, отправляет пользователю письмо со ссылкой для сброса.
@router.post("/password-reset")
def password_reset():
    return

# для проверки токена сброса пароля (обычно через ссылку в письме).
@router.get("/password-reset/{token}")
def password_reset():
    return

# для подтверждения нового пароля с использованием токена сброса.
@router.post("/password-reset/confirm")
def password_reset_confirm():
    return

@router.get("/profile")
async def profile(
    token: str, 
    response: Response,
    session: AsyncSession = Depends(get_async_session)
):
    user = await validate_token(token, session, response)
    if user is False:
        raise HTTPException(status_code=400, detail="Invalid token")
    else:
        user = await return_user(user)
        return user

@router.put("/profile")
def profile():
    return

@router.post("/logout")
def logout():
    return