from sqlalchemy import create_engine
from app.config import POSTGRES_LINK


class Connection:
    postgres_database = POSTGRES_LINK

    @staticmethod
    def get_engine():
        """Create connection to db"""
        # create engine
        engine = create_engine(Connection.postgres_database)
        return engine
