# This is to manage pydentic schemas.

from pydantic import BaseModel


class CreateUser(BaseModel):
    """Create user request schema."""
    username: str
    password_hash: str
    email: str
    first_name: str
    last_name: str


class AssignUserRole(BaseModel):
    """Schema for API to assign role to a user."""
    user_id: int
    role_id: int
