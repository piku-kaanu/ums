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

1. User creation API: POST: /users/create
   - this API will create user with unique username.
2. User updation API: PUT: /users/<user_id>
   - This API will update existing user.
3. User deletion API: DELETE: /users/<user_id>
   - This API will delete existing user.
4. User fetch API: GET: /users/<user_id>
   - This API will fetch existing user.
5. Assign a role to a user: /assign_role
   - This API will assign a specific role to a specific user.

## Contributing
- v1.0: Parth Kansara: Added CRUD APIs for user and an API to assign the role to a user.

