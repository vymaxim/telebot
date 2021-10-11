
from sqlalchemy import Column, Integer, String, Date, inspect
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Post(Base):

    __tablename__ = 'plants'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(512),)
    watering_at = Column(Date,)
    watering_period = Column(Integer)
    next_watering_at = Column(Date,)
    fertilization_at = Column(Date,)
    fertilization_period = Column(Integer)
    next_fertilization__at = Column(Date,)


def table_exists(engine):
    table_names = inspect(engine).has_table('plants')
    return table_names


def create_database(engine):
    conn = engine.connect()
    if not table_exists(engine):
        Base.metadata.create_all(engine)
    conn.close()

