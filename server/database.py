from sqlalchemy import create_engine
from models import Base
import os

def init_db():
    """Initialize the database and create tables."""
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()

# TODO:
# Admin GUI for handling database and server commands
