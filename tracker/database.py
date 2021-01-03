from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column("username", String(32))
    lifts = relationship("Lift")


class Lift(Base):
    __tablename__ = "lifts"
    id = Column(Integer, primary_key=True)
    exercise = Column("exercise", String(64))
    category = Column("category", String(32))
    weight = Column("weight", Numeric)
    reps = Column("reps", Integer)
    orm = Column("orm", Numeric)
    date = Column("date", Date)
    user_id = Column(Integer, ForeignKey("users.id"))


def start_db(sql_db_file: str):
    # https://ondras.zarovi.cz/sql/demo/
    engine = create_engine(f"sqlite:///{sql_db_file}", echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


def add_data():
    a = 1
