import uuid
from datetime import datetime, timedelta
from enum import auto

from passlib.handlers.bcrypt import bcrypt
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from actions.db.tables import Base
from actions.helpers import AutoNameEnum


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean(), nullable=False)
    email = Column(String(255), unique=True)
    api_key = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))

    devices = relationship("Device")
    tokens = relationship("Token")

    def check_password(self, password):
        return bcrypt.verify(password, self.password)

    def set_password(self, password):
        self.password = bcrypt.hash(password)

    def as_dict(self):
        return {
            "id": self.id,
            "is_active": self.is_active,
            "email": self.email,
            "username": self.username,
            "api_key": self.api_key,
        }


class TokenType(AutoNameEnum):
    authorization_code = auto()
    access_token = auto()
    refresh_token = auto()


class Token(Base):
    __tablename__ = "token"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(TokenType))
    code = Column(String(255), unique=True)
    expires_on = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", foreign_keys=[user_id])

    def set_ttl(self, live_time_in_seconds):
        self.expires_on = datetime.now() + timedelta(seconds=live_time_in_seconds)

    @hybrid_property
    def is_expired(self):
        if self.expires_on:
            return datetime.now() > self.expires_on
        return False
