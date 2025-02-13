# This is the main api entry module.

from fastapi import FastAPI, status, Depends, HTTPException
from logging import getLogger
from sqlalchemy.orm import Session

from utils.container import get_db
from utils.models import Users, Permissions, RolePermissions, Roles, UserRoles
from utils.schemas import CreateUser, AssignUserRole


app = FastAPI()
logger = getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """This is the server start up event function.
    In this function, we will do following if needed. It depends on the end user's response.
        1. Create superuser permission if not exists.
        2. Create superuser role if not exists.
        3. Create superuser permission and role relation if not exists.
        4. Asks for Username and Password of the superuser and create a superuser.
        5. Assign the superuser role to newly created superuser.
    """
    logger.info("Starting the server...")
    create_super_user = input("Create a new super user[y/n]?[n]: ")
    if create_super_user.lower() == 'y':
        db = next(get_db())
        logger.info("Fetching 'all' permission...")
        all_permissions = db.query(Permissions).filter(Permissions.permission_name == "all").first()
        if all_permissions is None:
            logger.info("'all' permission not found.\nCreating 'all' permission...")
            all_permissions = Permissions(**{"permission_name": "all"})
            db.add(all_permissions)
            db.commit()
            db.refresh(all_permissions)
            logger.info("'all' permission created.")
        else:
            logger.info("'all' permission found.")
        logger.info("Fetching admin role...")
        admin_role = db.query(Roles).filter(Roles.role_name == "admin").first()
        if admin_role is None:
            logger.info("admin role not found.\n Creating admin role...")
            admin_role = Roles(**{"role_name": "admin"})
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            logger.info("admin role created.")
        else:
            logger.info("admin role found.")
        logger.info("Fetching role permission...")
        role_permission = db.query(RolePermissions).\
            filter(RolePermissions.role_id == admin_role.role_id).\
            filter(RolePermissions.permission_id == all_permissions.permission_id).first()
        if role_permission is None:
            logger.info("Role permission not found.\nCreating new role permission...")
            role_permission = RolePermissions(
                **{"role_id": admin_role.role_id, "permission_id": all_permissions.permission_id})
            db.add(role_permission)
            db.commit()
            db.refresh(role_permission)
            logger.info("Role permission created successfully.")
        else:
            logger.info("Role permission found.")
        logger.info("Creating super user.")
        user_name = input("Enter username: ")
        if not user_name:
            logger.error("Username is required.")
            exit(1)
        password = input("Enter password: ")
        if not password:
            logger.error("Password is required.")
            exit(1)
        new_user = db.query(Users).filter(Users.username == user_name).filter(Users.status == "active").first()
        if new_user:
            logger.error(f"User {user_name} exists.")
            exit(0)
        new_user = Users(**{"username": user_name, "password_hash": password, "status": "active"})
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info("New super user created...")
        logger.info("Applying the role to super user...")
        role_user = UserRoles(**{"user_id": new_user.user_id, "role_id": admin_role.role_id})
        db.add(role_user)
        db.commit()
        db.refresh(role_user)
        logger.info("Role assigned to super user. ")
    else:
        logger.info("Moving forward without creating super user.")

    logger.info("Good to go...\nStarting the server...")


@app.get("/healthcheck")
async def healthcheck():
    """Healthcheck API. useful for checking server health after deployment."""
    return {"message": "Server Health is good!"}


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: CreateUser, db: Session = Depends(get_db)):
    """User creation API."""
    try:
        logger.info("Started creating the new user.")
        new_user = Users(**user_request.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"New user created successfully: {new_user.username}")
        return {
            "user_name": user_request.username,
            "message": f"User {user_request.username} created successfully!"
        }
    except Exception as error:
        logger.error(f"Failure while creating a new user: {user_request.username}: {error}")
        if "already exists" in str(error):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_request.username} already exists!"
            )


@app.put("/users/{user_id}")
async def update_user(user_id: int, user_request: CreateUser, db: Session = Depends(get_db)):
    """Update API for the existing user."""
    try:
        logger.info(f"Updating the user: {user_id}")
        user = db.query(Users).filter(Users.user_id == user_id).filter(Users.status == "active")
        if user.first() is None:
            logger.error(f"Error: No active user found with {user_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
        user.update(user_request.dict(), synchronize_session=False)
        db.commit()
        logger.info(f"User details updated successfully! {user_id}")
        return {
            "user_id": user_id,
            "message": f"User deleted successfully!"
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
    except Exception as error:
        logger.error(f"Error in updating user {user_id}: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get API for the existing user."""
    try:
        logger.info(f"Fetching data for {user_id}.")
        user = db.query(Users).filter(Users.user_id == user_id).filter(Users.status == "active")
        if user.first() is None:
            logger.error(f"Error: No active user found with {user_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
        user_data = user.first()
        logger.info("Masking user password.")
        user_data.password_hash = "******"
        return {
            "user_id": user_id,
            "message": f"User found successfully!",
            "user_details": user.first()
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
    except Exception as error:
        logger.error(f"Error in fetching user {user_id}: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete API for the existing user. It will soft-delete the user."""
    try:
        logger.info(f"Fetching data for {user_id} to delete.")
        user = db.query(Users).filter(Users.user_id == user_id)
        if user.first() is None:
            logger.error(f"Error: No active user found with {user_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
        logger.info(f"Setting the status as inactive for the user {user_id}")
        user.update({"status": "inactive"}, synchronize_session=False)
        db.commit()
        logger.info(f"User {user_id} soft deleted successfully!")
        return {
            "user_id": user_id,
            "message": f"User deleted successfully!"
        }
    except HTTPException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except Exception as error:
        logger.error(f"Error in deleting user {user_id}: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@app.post("/assign_role")
async def role_assignment(user_request: AssignUserRole, db: Session = Depends(get_db)):
    """This API will assign the provided role to provided user."""
    try:
        logger.info(f"Fetching data for user {user_request.user_id}.")
        user = db.query(Users).filter(Users.user_id == user_request.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found!")
        logger.info(f"Fetching data for role {user_request.role_id}.")
        role = db.query(Roles).filter(Roles.role_id == user_request.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Role not found!")
        logger.info(f"Checking if role {role.role_name} to user {user.username} already assigned.")
        user_role = db.query(UserRoles).\
            filter(UserRoles.user_id == user_request.user_id).\
            filter(UserRoles.role_id == user_request.role_id).first()
        if user_role:
            logger.info(f"Role {role.role_name} already assigned to user {user.username}")
            return {
                "user_name": user.username,
                "role": role.role_name,
                "message": f"Role already has been assigned!"
            }
        logger.info(f"Assigning Role {role.role_name} to user {user.username}.")
        user_role = UserRoles(**{"user_id": user.user_id, "role_id": role.role_id})
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        logger.info(f"Role {role.role_name} assigned to user {user.username}")
        return {
            "user_name": user.username,
            "role": role.role_name,
            "message": f"Role {role.role_name} has been assigned to the user {user.username} successfully!"
        }
    except HTTPException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except Exception as error:
        logger.error(f"Error in assigning role {user_request.role_id} to user {user_request.user_id}: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
