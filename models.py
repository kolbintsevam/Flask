from atexit import register

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

PG_USER = "My_app_ads"
PG_PASSWORD = "111a"
PG_DB = "My_app_ads"
PG_HOST = "127.0.0.1"
PG_PORT = 5430
PG_DSN = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(PG_DSN)

register(engine.dispose)

Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())

class Ads(Base):
    __tablename__ = "Ads"

    id = Column(Integer, primary_key=True)
    title = Column(String,nullable=False)
    description = Column(Text)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)

    owner = relationship(User, backref="Ads")

Base.metadata.create_all()

with Session() as session:
    user = session.query(User).filter_by(name = 'user_2').all()