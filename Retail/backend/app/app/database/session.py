from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


engine = create_engine("mysql+pymysql://root:@localhost/retail_main")
SessionLocal = sessionmaker( bind=engine) 