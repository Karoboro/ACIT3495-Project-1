from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
hostname = os.getenv("DB_HOSTNAME")
port = os.getenv("DB_PORT")
db = os.getenv("DATABASE")

DB_ENGINE = create_engine(f"mysql+mysqldb://{user}:{password}" +
                          f"@{hostname}:{port}/{db}")


def make_session():
    return sessionmaker(bind=DB_ENGINE)()


def drop_tables():
    Base.metadata.drop_all(DB_ENGINE)


Base.metadata.create_all(DB_ENGINE)


if __name__ == "__main__":
    drop_tables()
