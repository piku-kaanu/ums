# This will be handled via config files and loaded at the time of starting server.

# Database configurations
DB_USERNAME = "postgres"
DB_PASSWORD = "postgres"  # This can be stored in the AWS secure vault app.
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"

# Secret key for JWT encoding/decoding
SECRET_KEY = "your_secret_key"  # Here we can use custom generated secret key.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Logger
LOG_FILE = "app.log"
MAX_BYTES = 10 ** 6
BACKUP_COUNT = 3
