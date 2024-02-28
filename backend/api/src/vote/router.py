import re
from fastapi import APIRouter, Depends, Response
from fastapi import Depends
from httpx import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
# 
from database import get_async_session
from vote.models import voting, voting_model, voting_option, Voting
from vote.shemas import CreateVote
from user.functions import check_permission


router = APIRouter(
    prefix="/api/v1/vote",
    tags=["Vote"]
)


@router.post("/create_voting/")
async def create_voting(vote_name: CreateVote, token: str, response: Response, session: AsyncSession = Depends(get_async_session)):
    has_permission = await check_permission(token, session, response)
    
    if has_permission and "delete" in has_permission:
        if has_permission["delete"]:
            async def create_new_voting(session: AsyncSession):
                stmt = insert(voting).values(**vote_name.dict())
                await session.execute(stmt)
                await session.commit()
                return {"status": "success"}
            return await create_new_voting(session)
        else:
            return {"у вас нет прав на создание"}
    else:
        return {"Ошибка: недостаточно прав или неверный токен"}


@router.get("/get/vote")
async def get_votes(token: str, response: Response, session: AsyncSession = Depends(get_async_session)):
    has_permission = await check_permission(token, session, response)
    
    if has_permission and "delete" in has_permission:
        if has_permission["delete"]:
            async def vote(session: AsyncSession):
                query = select(voting)
                result = await session.execute(query)
                votes = result.mappings().all()
                return votes
            return await vote(session)
        else:
            return {"у вас нет прав на чтение"}
    else:
        return {"Ошибка: недостаточно прав или неверный токен"}


@router.delete("/delete/{id}")
async def delete_vote_id(id: int, token: str, response: Response, session: AsyncSession = Depends(get_async_session)):
    has_permission = await check_permission(token, session, response)
    
    if has_permission and "delete" in has_permission:
        if has_permission["delete"]:
            async def delete_voting(session: AsyncSession):
                query = delete(voting).where(voting.c.id == id)
                await session.execute(query)
                await session.commit()
                return {"deleted": id}
            return await delete_voting(session)
        else:
            return {"у вас нет прав на удаление"}
    else:
        return {"Ошибка: недостаточно прав или неверный токен"}
    

@router.get("/")
async def get(token: str, response: Response, session: AsyncSession = Depends(get_async_session)):
    has_permission = await check_permission(token, session, response)
    
    if has_permission and "delete" in has_permission:
        if has_permission["delete"]:
            return {"у вас ЕСТЬ права на удаление"}
        else:
            return {"у вас НЕТ прав на удаление"}
    else:
        return {"Ошибка: недостаточно прав или неверный токен"}
             