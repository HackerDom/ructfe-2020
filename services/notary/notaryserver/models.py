#!/usr/bin/env python3

import json

from flask_sqlalchemy import SQLAlchemy

from notary import Notary, serialize_bytes, deserialize_bytes


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    public_key = db.Column(db.String, nullable=False)
    private_key = db.Column(db.String, nullable=False)
    documents = db.relationship('Document', backref='author', lazy=True)

    def __init__(self, username, name, phone, address):
        self.username = username
        self.name = name
        self.phone = phone
        self.address = address
        self.private_key = Notary.generate_private_key()
        self.public_key = Notary.get_public_key(self.private_key)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def generate_password(self):
        return Notary.sign(self.private_key, 'user', self.username)

    def verify_password(self, password):
        return Notary.verify(self.public_key, 'user', self.username, password)

    def __repr__(self):
        return f'<User {self.username} (id={self.id})>'


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    signature = db.Column(db.String, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False)

    def __init__(self, author, title, text, is_public):
        self.author_id = author.id
        self.title = title
        self.text = text
        self.signature = Notary.sign(author.private_key, title, text)
        self.is_public = is_public

    def generate_password(self):
        obj = {'documents': [self.id]}
        obj_data = serialize_bytes(json.dumps(obj).encode('utf-8'))
        
        signature = Notary.sign(self.author.private_key, 'document', obj_data)
        
        return f'{obj_data}.{signature}'

    def verify_password(self, password):
        try:
            obj_data, signature = password.split('.')
            obj = json.loads(deserialize_bytes(obj_data).decode('utf-8'))
        except ValueError:
            return False
        
        if not Notary.verify(self.author.public_key, 'document', obj_data, signature):
            return False
        
        documents = obj.get('documents')

        if documents is None or not isinstance(documents, list):
            return False

        return self.id in documents
        

    def __repr__(self):
        return f'<Document #{self.id} by {self.author.username} (author_id={self.author_id})>'
