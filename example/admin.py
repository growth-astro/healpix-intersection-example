from .models import db

def create_all():
    db.reflect()
    db.drop_all()
    db.session.commit()
    db.create_all()
