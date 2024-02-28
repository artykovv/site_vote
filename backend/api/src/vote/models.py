from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
# from src.user.models import user
from user.models import user
from sqlalchemy.orm import relationship

metadata = MetaData()

voting = Table(
    'voting', metadata,
   Column('id', Integer, primary_key=True, autoincrement=True),
   Column('name', String),
    
)
voting_option = Table(
    'voting_option', metadata,
   Column('id', Integer, primary_key=True, autoincrement=True),
   Column('name', String),
   Column("voting_id", Integer, ForeignKey(voting.c.id)),
)
uservote = Table(
    'uservote', metadata,
   Column('id', Integer, primary_key=True, autoincrement=True),
   Column("user_id", Integer, ForeignKey(user.c.id)),
   Column("option_id", Integer, ForeignKey(voting_option.c.id)),    
)


class Voting:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.options = []

class VotingOption:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class UserVote:
    def __init__(self, id, user_id, option_id):
        self.id = id
        self.user_id = user_id
        self.option_id = option_id

voting_model = relationship("Voting", back_populates="options")
voting_option_model = relationship("VotingOption", back_populates="voting")
user_vote_model = relationship("UserVote", back_populates="option")
