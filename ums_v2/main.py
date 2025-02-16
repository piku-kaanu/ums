from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from container import get_db
from app_logger import logging
from models import Users, Assets, UserRoles, Roles
from schemas import User, UserLogin, AssignUserRole
from user_auth import get_password_hash, verify_password, create_access_token, get_permission

app = FastAPI()


@app.get("/healthcheck")
def read_root():
    return {"message": "heathcheck: Everything looks good!"}


@app.post("/users/v1/register")
def register(user: User, db: Session = Depends(get_db)):
    try:
        logging.info(f"Registration for user '{user.username}' starts.")
        logging.info(f"Checking if username already exists.")
        user_obj = db.query(Users).filter(Users.username == user.username).first()
        if user_obj:
            logging.error(f"User '{user.username}' already exists.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        hashed_password = get_password_hash(user.password)
        user.password = hashed_password
        logging.info(f"Start storing user details in the users table for '{user.username}'.")
        user_obj = Users(**user.dict())
        db.add(user_obj)
        db.commit()
        logging.info(f"User '{user.username}' registered successfully!")
        return {"message": "User registered successfully"}
    except HTTPException as error:
        return {"message": str(error)}
    except Exception as error:
        logging.error(f"Error while storing '{user.username}': {str(error)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


@app.post("/users/v1/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        logging.info(f"Trying to login user '{user.username}'.")
        logging.info(f"Checking user '{user.username}' in the database.")
        user_obj = db.query(Users).filter(Users.username == user.username).first()
        if not user_obj:
            logging.error(f"User '{user.username}' not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not registered")
        if not user_obj.password or not verify_password(user.password, user_obj.password):
            logging.error(f"Credentials not correct for user '{user.username}'")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        logging.info(f"User credentials are correct. Creating bearer token.")
        access_token = create_access_token(data={"sub": user.username})
        logging.info(f"User {user.username} logged in successfully.")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as error:
        return {"message": str(error)}
    except Exception as error:
        logging.error(f"Error while logging {user.username} in: {str(error)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


@app.post("/assign_role")
async def role_assignment(request: Request, user_request: AssignUserRole, db: Session = Depends(get_db)):
    """This API will assign the provided role to provided user."""
    try:
        logging.info(f"Assigning role to user.")
        logging.info(f"Checking if session user has permission to assign role.")
        is_permitted = get_permission(request.headers.get("authorization"), 'admin', db)
        if not is_permitted:
            logging.error("Session user is not permitted to assign roles.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Access denied!")
        logging.info(f"Fetching data for user {user_request.user_id}.")
        user = db.query(Users).filter(Users.user_id == user_request.user_id).first()
        if not user:
            logging.error(f"User not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
        logging.info(f"Fetching data for role {user_request.role_id}.")
        role = db.query(Roles).filter(Roles.role_id == user_request.role_id).first()
        if not role:
            logging.error("Role not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Role not found!")
        logging.info(f"Checking if role {role.role_name} to user {user.username} already assigned.")
        user_role = db.query(UserRoles).\
            filter(UserRoles.user_id == user_request.user_id).\
            filter(UserRoles.role_id == user_request.role_id).first()
        if user_role:
            logging.error(f"Role {role.role_name} already assigned to user {user.username}")
            return {
                "user_name": user.username,
                "role": role.role_name,
                "message": f"Role already has been assigned!"
            }
        logging.info(f"Assigning Role {role.role_name} to user {user.username}.")
        user_role = UserRoles(**{"user_id": user.user_id, "role_id": role.role_id})
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        logging.info(f"Role {role.role_name} assigned to user {user.username}")
        return {
            "user_name": user.username,
            "role": role.role_name,
            "message": f"Role {role.role_name} has been assigned to the user {user.username} successfully!"
        }
    except HTTPException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except Exception as error:
        logging.error(f"Error in assigning role {user_request.role_id} to user {user_request.user_id}: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@app.get("/assets/v1/business")
def get_business(request: Request, db: Session = Depends(get_db)):
    try:
        logging.info("Getting secret business data.")
        logging.info("Checking if the session user is permitted to read business data.")
        is_permitted = get_permission(request.headers.get('authorization'), "admin", db)
        if not is_permitted:
            logging.error("Session user is not permitted to read business data.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                          detail="Access denied!")
        logging.info("Fetching business data from db.")
        business_data = db.query(Assets).filter(Assets.is_secret == True).first()
        logging.info("Returning business data.")
        return business_data
    except HTTPException as error:
        return {"message": str(error)}
    except Exception as error:
        logging.error(f"Error in fetching business data: {str(error)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


@app.get("/assets/v1/marketing")
def get_marketing(request: Request, db: Session = Depends(get_db)):
    try:
        logging.info("Getting Marketing data.")
        logging.info("Checking if the session user is permitted to read marketing data.")
        is_permitted = get_permission(request.headers.get('authorization'), "staff", db)
        if not is_permitted:
            logging.error("Session user is not permitted to read marketing data.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Access denied!")
        logging.info("Fetching business data from db.")
        business_data = db.query(Assets).filter(Assets.is_secret == False).first()
        logging.info("Returning business data.")
        return business_data
    except HTTPException as error:
        return {"message": str(error)}
    except Exception as error:
        logging.error(f"Error in fetching marketing data: {str(error)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))
