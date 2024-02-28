from pydantic import BaseModel


class CreateVote(BaseModel):
    name: str
