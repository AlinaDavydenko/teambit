import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
PORT = 5432

POSTGRES_LINK = f"postgresql://{DB_USER}:{DB_PASSWORD}@postgres:{PORT}/{DB_NAME}"

# JSON Web Tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
