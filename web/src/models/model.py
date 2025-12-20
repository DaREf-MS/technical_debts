from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, DateTime, Boolean, Table
)
from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid
from src.models import db
from typing import TypeAlias
from src.utilities.value_range import ValueRange
from flask_login import UserMixin

ID : TypeAlias = str

class ModelMixin:
    def as_dict(self, include_relationships: bool = True):
        mapper = inspect(self.__class__)
        result = {}
        for column in mapper.columns:
            key = column.key
            val = getattr(self, key)
            if isinstance(val, enum.Enum):
                result[key] = val.value
            elif isinstance(val, datetime):
                result[key] = val.isoformat()
            else:
                result[key] = val
        if include_relationships:
            for rel in mapper.relationships:
                name = rel.key
                try:
                    value = getattr(self, name)
                except Exception:
                    value = None
                if value is None:
                    result[name] = None
                else:
                    if rel.uselist:
                        result[name] = [
                            item.as_dict(include_relationships=False) if hasattr(item, 'as_dict') else str(item)
                            for item in value
                        ]
                    else:
                        result[name] = value.as_dict(include_relationships=False) if hasattr(value, 'as_dict') else str(value)
        return result


# ---------------- CORE TABLES ---------------- #

class Duplication(ModelMixin, db.Model): 
    __tablename__ = "duplication"
    # PK
    id = Column(String(36), primary_key = True)
    
    # FK
    code_fragment_id = Column(String(36), ForeignKey("code_fragment.id"))
    file_id = Column(String(36), ForeignKey("file.id"))

    # Columns
    line_count = Column(Integer)
    from_line = Column(Integer)
    to_line = Column(Integer)
    from_column = Column(Integer)
    to_column = Column(Integer)

    def __init__(self, code_fragment_id : str, file_id : str, line_count : int, line_domain : ValueRange, column_domain : ValueRange): 
        self.id = str(uuid.uuid4())
        self.code_fragment_id = code_fragment_id
        self.file_id = file_id
        self.line_count = line_count
        self.from_line = line_domain.From
        self.to_line = line_domain.To
        self.from_column = column_domain.From
        self.to_column = column_domain.To
        return
    
    def lines(self) -> ValueRange: 
        return ValueRange(self.from_line, self.to_line)
    
    def columns(self) -> ValueRange: 
        return ValueRange(self.from_column, self.to_column)

class CodeFragment(ModelMixin, db.Model): 
    __tablename__ = "code_fragment"
    # PK
    id = Column(String(36), primary_key = True)

    # Columns
    text = Column(Text)
    line_count = Column(Integer)

    def __init__(self, text: str, line_count: int):
        self.id = str(uuid.uuid4())
        self.text = text
        self.line_count = line_count
        return

class Repository(ModelMixin, db.Model):
    __tablename__ = "repository"
    id = Column(String(36), primary_key=True)
    owner = Column(Text, nullable=False)
    name = Column(Text, nullable=False)

class Branch(ModelMixin, db.Model):
    __tablename__ = "branch"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)

    repository_id = Column(String(36), ForeignKey("repository.id"))


class Commit(ModelMixin, db.Model):
    __tablename__ = "commit"
    id = Column(String(36), primary_key=True)
    sha = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    author = Column(Text, nullable=False)
    message = Column(Text, nullable=True)

    branch_id = Column(String(36), ForeignKey("branch.id"))


class File(ModelMixin, db.Model):
    __tablename__ = "file"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)

    commit_id = Column(String(36), ForeignKey("commit.id"))

class Function(ModelMixin, db.Model):
    __tablename__ = "function"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)
    line_position = Column(Integer)

    file_id = Column(String(36), ForeignKey("file.id"))


class IdentifiableEntity(ModelMixin, db.Model):
    __tablename__ = "identifiable_entity"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)


class FileIdentifiableEntity(ModelMixin, db.Model):
    __tablename__ = "file_identifiable_entity"

    id = Column(String(36), primary_key=True)
    file_id = Column(String(36), ForeignKey("file.id"))
    identifiable_entity_id = Column(String(36), ForeignKey("identifiable_entity.id"))
    line_position = Column(Integer)


class IdentifiableEntityCount(ModelMixin, db.Model):
    __tablename__ = "identifiable_entity_count"
    id = Column(String(36), primary_key=True)
    count = Column(Integer)

    identifiable_entity_id = Column(String(36), ForeignKey("identifiable_entity.id"))
    commit_id = Column(String(36), ForeignKey("commit.id"))


class ComplexityCount(ModelMixin, db.Model):
    __tablename__ = "complexity_count"
    id = Column(String(36), primary_key=True)
    total_complexity = Column(Integer)
    function_count = Column(Integer)
    average_complexity = Column(Float)

    commit_id = Column(String(36), ForeignKey("commit.id"))

class Complexity(ModelMixin, db.Model):
    __tablename__ = "complexity"
    id = Column(String(36), primary_key=True)
    value = Column(Integer)

    function_id = Column(String(36), ForeignKey("function.id"))


# ---------------- AUTHENTICATION & AUTHORIZATION TABLES ---------------- #

class User(UserMixin, ModelMixin, db.Model):
    """User account model"""
    __tablename__ = "user"
    
    id = Column(String(36), primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    reset_token = Column(String(255))
    reset_token_expiry = Column(DateTime)
    
    # Relationships
    repository_access = relationship("RepositoryAccess", foreign_keys="RepositoryAccess.user_id", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, username, email, password_hash, first_name=None, last_name=None, is_admin=False):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        self.is_active = True
        self.created_at = datetime.utcnow()
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'


class RepositoryAccess(ModelMixin, db.Model):
    """Association table for user-repository access control"""
    __tablename__ = "repository_access"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    repository_id = Column(String(36), ForeignKey("repository.id"), nullable=False)
    can_read = Column(Boolean, default=True, nullable=False)
    can_write = Column(Boolean, default=False, nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    granted_by_id = Column(String(36), ForeignKey("user.id"))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="repository_access")
    repository = relationship("Repository")
    granted_by = relationship("User", foreign_keys=[granted_by_id])
    
    def __init__(self, user_id, repository_id, can_read=True, can_write=False, granted_by_id=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.repository_id = repository_id
        self.can_read = can_read
        self.can_write = can_write
        self.granted_by_id = granted_by_id
        self.granted_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<RepositoryAccess user={self.user_id} repo={self.repository_id}>'

