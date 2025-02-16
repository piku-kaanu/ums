from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Union

from constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app_logger import logging
from models import Users, Roles, UserRoles


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password, hashed_password):
    logging.info("Verifying password.")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    logging.info("Hashing password.")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    logging.info("Creating access token.")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    logging.info("Adding expiring time of token.")
    to_encode.update({"exp": expire})
    logging.info("Encoding the token.")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    logging.info("Decoding the token.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload["exp"] >= datetime.utcnow().timestamp() else None
    except JWTError:
        logging.error("Error in decoding JWT token.")
        return None


def get_permission(token: str, role: str, db) -> bool:
    """This function will return True if the user is permitted."""
    # TODO: We can use caching mechanism as following.
    # Flow will be like,
    # Check if provided token is available,
    # if available then return True or False based on the comparison of provided role and cached role.
    # if not available then fetch the data from db,
    # store data in cache in this pattern {<token>: {"username": <username>, "role": <role_name>}}
    # Keep Threshold time same as JWT Token expiry time. This way stale token will be removed automatically.

    logging.info("Validating user permission.")
    if not token:
        logging.error("Token not found.")
        return False
    decoded_token = decode_access_token(token.replace("Bearer ", ""))
    if not decoded_token:
        logging.error("Invalid token.")
        return False
    user = decoded_token.get('sub', None)
    if not user:
        logging.error("username not found in token.")
        return False

    logging.info("Fetching user and role data from db.")
    user_obj = db.query(Users).filter(Users.username == user).first()
    user_role = db.query(UserRoles).filter(UserRoles.user_id == user_obj.user_id)

    # Return True for the Admin user.
    if user_role and user_role.first() and user_role.first().role_id == 1:
        logging.info("User is an admin user.")
        return True

    logging.info("Checking user's role.")
    role_obj = db.query(Roles).filter(Roles.role_name == role).first()
    user_role = user_role.filter(UserRoles.role_id == role_obj.role_id).first()

    return bool(user_role)
