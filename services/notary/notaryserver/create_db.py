#!/usr/bin/env python3

from app import app
from models import db, User, Document


with app.app_context():
    db.create_all()
    u = User('qwer', 'Qwer Qwer', '+1234', 'addr')
    db.session.add(u)
    db.session.commit()
    print(f'qwer\'s password is "{u.generate_password()}"')
    for i in range(115):
        db.session.add(Document(u, f'title{i}', f'text{i}'))
    db.session.commit()
