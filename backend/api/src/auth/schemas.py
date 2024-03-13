from pydantic import BaseModel
class CreateUser(BaseModel):
    username: str
    email: str
    password: str

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class ReadUser(BaseModel):
    username: str 
    email: str

class EditPassword(BaseModel):
    old_password: str
    new_password: str