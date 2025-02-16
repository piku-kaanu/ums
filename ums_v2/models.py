# This is the ORM model module.

from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import DeclarativeBase

from container import engine


class Base(DeclarativeBase):
    pass


class Users(Base):
    """User model"""
    __table__ = Table(
        'users',
        Base.metadata,
        Column('user_id', Integer, primary_key=True),
        autoload_with=engine
    )


class Assets(Base):
    """User model"""
    __table__ = Table(
        'assets',
        Base.metadata,
        Column('id', Integer, primary_key=True),
        autoload_with=engine
    )


class Permissions(Base):
    """Permissions model"""
    __table__ = Table(
        'permissions',
        Base.metadata,
        Column('permission_id', Integer, primary_key=True),
        autoload_with=engine
    )


class Roles(Base):
    """Role model"""
    __table__ = Table(
        'roles',
        Base.metadata,
        Column('role_id', Integer, primary_key=True),
        autoload_with=engine
    )


class RolePermissions(Base):
    """Role Permission relation model"""
    __table__ = Table(
        'role_permissions',
        Base.metadata,
        autoload_with=engine
    )


class UserRoles(Base):
    """User Role relation model"""
    __table__ = Table(
        'user_roles',
        Base.metadata,
        autoload_with=engine
    )
