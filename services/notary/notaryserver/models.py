#!/usr/bin/env python3

import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import UUIDType

from notary import Notary, pack_document, load_document, serialize_bytes, deserialize_bytes


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    public_key = db.Column(db.String, nullable=False)
    private_key = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    documents = db.relationship('Document', backref='author', lazy=True, cascade="all, delete")

    def __init__(self, username, name, phone, address):
        self.username = username
        self.name = name
        self.phone = phone
        self.address = address
        self.private_key = Notary.generate_private_key()
        self.public_key = Notary.get_public_key(self.private_key)
        self.timestamp = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def generate_password(self):
        return Notary.sign(self.private_key, self.username.encode('utf-8'))

    def verify_password(self, password):
        return Notary.verify(self.public_key, self.username.encode('utf-8'), password)

    def __repr__(self):
        return f'<User {self.username} (id={self.id})>'


class Document(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    author_id = db.Column(UUIDType(), db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)
    signature = db.Column(db.String, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, author, title, text, is_public):
        self.author_id = author.id
        self.title = title
        self.text = text
        self.is_public = is_public
        self.signature = Notary.sign(author.private_key, pack_document(title, text))
        self.timestamp = datetime.utcnow()

    def generate_password(self):
        document = pack_document('document_id', str(self.id))
        signature = Notary.sign(self.author.private_key, document)
        
        return f'{serialize_bytes(document)}.{signature}'

    def verify_password(self, password):
        try:
            document_data, signature = password.split('.')
            document = deserialize_bytes(document_data)
            title, text = load_document(document)
        except ValueError:
            return False
        
        if not Notary.verify(self.author.public_key, document, signature):
            return False

        return title == 'document_id' and text == str(self.id)

    def __repr__(self):
        return f'<Document #{self.id} by {self.author.username} (author_id={self.author_id})>'
