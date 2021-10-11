import datetime


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Post, create_database


def create_connection():
    engine = create_engine('sqlite:///sqlite3.db')
    create_database(engine)
    global Session
    Session = sessionmaker(bind=engine)


def add_into_db(plant):
    session = Session()
    plant.next_watering_at = plant.watering_at + datetime.timedelta(days=plant.watering_period)
    plant.next_fertilization__at = plant.fertilization_at + datetime.timedelta(days=plant.fertilization_period)
    session.add(plant)
    session.commit()


def get_plants_id_name():
    session = Session()
    plants_id_name = session.query(Post.id, Post.name).all()
    session.close()
    return plants_id_name


def get_plants_info():
    session = Session()
    plants_id_name = session.query(Post.id, Post.name, Post.next_watering_at, Post.next_fertilization__at).all()
    session.close()
    return plants_id_name


def update_time(id, watering=None, fertilization=None):
    session = Session()
    plant = session.query(Post).get(Post.id == id)
    if watering:
        plant.watering_at = plant.next_watering_at
        plant.next_watering_at += datetime.timedelta(days=plant.watering_period)
    if fertilization:
        plant.fertilization = plant.next_fertilization_at
        plant.next_fertilization_at += datetime.timedelta(days=plant.fertilization_period)


def get_choice(option, id):
    session = Session()
    choice = ''
    if option == 'description':
        choice = session.query(Post.description).filter(Post.id == id)
    if option == 'next_watering_at':
        choice = session.query(Post.next_watering_at).filter(Post.id == id)
    if option == 'next_fertilization_at':
        choice = session.query(Post.next_fertilization__at).filter(Post.id == id)
    session.close()
    return choice


def delete_plant_in_database(id):
    session = Session()
    plant = session.query(Post).get(id)
    session.delete(plant)
    session.commit()
    session.close()


def change_info_in_database(option, id, text):
    session = Session()
    plant = session.query(Post).get(id)
    if option == 'name':
        plant.name = text
    elif option == 'description':
        plant.description = text
    elif option == 'watering_period':
        plant.watering_period = int(text)
        plant.next_watering_at = plant.watering_at + datetime.timedelta(days=plant.watering_period)
    elif option == 'fertilization_period':
        plant.fertilization_period = int(text)
        plant.next_fertilization__at = plant.fertilization_at + datetime.timedelta(days=plant.fertilization_period)
    session.commit()
    session.close()
