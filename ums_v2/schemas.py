from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str


class AssignUserRole(BaseModel):
    """Schema for API to assign role to a user."""
    user_id: int
    role_id: int
