from sqlmodel import Session, create_engine
from utils.config import settings

# Database engine with connection pool
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_size=10,        # Number of connections to keep in the pool
    max_overflow=20,     # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,     # Timeout for getting a connection from the pool
    pool_recycle=3600,   # Recycle connections after this many seconds
    pool_pre_ping=True   # Check connection health before using
)

def get_session():
    with Session(engine) as session:
        yield session

