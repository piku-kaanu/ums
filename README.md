# User Management System

This system is responsible for user management based on the assigned permissions and roles.
This system will also do authentication and authorization based on the assigned role.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Contributing](#contributing)

## Installation

For installation, follow below mentioned steps,
1. Install [Python 3.10](https://www.python.org/downloads/release/python-31015/).
2. Install virtualenv: pip install virtualenv
3. Create a new virtual environment: virtualenv venv
4. Activate virtual environment:
   1. Windows: venv\Scripts\activate
   2. Linux/Mac: source venv/bin/activate
5. Install all required packages: pip install -r requirements.txt
6. Install [Postgres](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
7. Setup the local database and update following in the src/utils/constants.py file.
   1. host
   2. port
   3. username
   4. password
   5. database name
8. Run create_tables.sql file to create required tables.
9. Start server: uvicorn main:app --reload

### Prerequisites

- Make sure you have completed all the steps mentioned in the [Installation](#Installation)
- Make suer you are using x86 or x64 system.

## Usage

1. User registration API: POST: /users/v1/register
   - this API will create user with unique username.
2. User login API: POST: /users/v1/login
   - This API will login user and create access token.
   - This access token can be used in the upcoming api calls.
   - This token will be active for 30 minutes.
3. Role Assignment API: POST: /assign_role
   - This API will check if the session user's role as admin.
   - If it is admin then it will assign the input role to the input user.
4. Business asset access: GET: /assets/v1/business
   - This API is the example to check role based access.
   - This API will return the business asset data only to the logged in admin user.
   - This will be checked from the bearer token from the request header. 
5. Marketing asset access: GET: /assets/v1/marketing
   - This API is the example to check role based access.
   - This API will return the marketing asset data to Staff and Admin users.
   - This will be checked from the bearer token from the request header.

## Contributing
- v1.0: Parth Kansara: Added CRUD APIs for user and an API to assign the role to a user.
- v1.1: Parth Kansara: Added ums_v2 app for user registration, user login and role based permission management.

## Future Enhancement
- Permissions will be further broken to Read, Write, Update and Delete.
- Various Roles can be defined to updated permissions on different assets.
- List of users will be shown with asset wise permissions.
- Admin user then can update any user details and permissions.

