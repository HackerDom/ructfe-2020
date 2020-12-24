#!/usr/bin/env python3

from app import app
from models import db, Document, User


with app.app_context():
    db.create_all()

    for i in range(10):
        user = User(f'user{i}', f'User{i} Name{i}', f'+1234{i}', f'Address{i}')
        
        db.session.add(user)
        db.session.commit()

        print(f'{user.username}\'s password is "{user.generate_password()}"')
        
        public_document = Document(user, f'public title{i}', f'public text{i}', True)
        db.session.add(public_document)
        
        private_document = Document(user, f'private title{i}', f'private text{i}', False)
        db.session.add(private_document)
        
        db.session.commit()
