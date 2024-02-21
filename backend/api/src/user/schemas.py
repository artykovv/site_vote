from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    email: str
    password: str

class TokenInfo(BaseModel):
    access_token: str
    token_type: str
