from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, JSON, Boolean
from datetime import datetime

metadata = MetaData()

role = Table(
   'role', metadata,
   Column('id', Integer, primary_key=True, autoincrement=True),
   Column('name', String),
   Column("permissions", JSON),
)

user = Table(
   'user', metadata, 
   Column('id', Integer, primary_key = True, autoincrement=True), 
   Column('username', String, unique=True, nullable=False), 
   Column('email', String, nullable=False),
   Column('password', String, nullable=False),
   Column('is_active', Boolean, default=True),
   Column("registered_at", DateTime, default=datetime.utcnow),
   Column("role_id", Integer, ForeignKey(role.c.id), default=1),
   UniqueConstraint('username', name='unique_username_constraint')
)
