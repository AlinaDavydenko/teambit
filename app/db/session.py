from sqlalchemy.orm import sessionmaker
from app.db.connection import Connection

engine = Connection.get_engine()
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()