from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    video_count = Column(Integer, default=0)

engine = create_engine(Config.DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def init_db():
    Base.metadata.create_all(engine)

def get_or_create_user(chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user is None:
        user = User(chat_id=chat_id, video_count=0)
        session.add(user)
        session.commit()
    return user

def increment_video_count(chat_id):
    user = get_or_create_user(chat_id)
    user.video_count += 1
    session.commit()

def create_custom_table():
    class CustomTable(Base):
        __tablename__ = 'custom_table'
        id = Column(Integer, primary_key=True)
        name = Column(String)
    Base.metadata.create_all(engine)

def get_all_users():
    return session.query(User).all()
