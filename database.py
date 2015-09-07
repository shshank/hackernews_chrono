from app_objects import db


def init_db():
    """
    call this function to create table in DB for any new class defined in the models.
    """
    import models
    db.create_all()
