from database import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = 'jwtusers'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False)
    hash_password = Column(String)
    