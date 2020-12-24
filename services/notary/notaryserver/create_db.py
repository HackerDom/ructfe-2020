from app import app
from models import db, User, Document


with app.app_context():
    db.create_all()
    u = User('qwer', '+1234', 'addr')
    db.session.add(u)
    db.session.commit()
    for i in range(115):
        db.session.add(Document(u, f'title{i}', f'text{i}'))
    db.session.commit()
