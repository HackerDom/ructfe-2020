#!/usr/bin/env python3

from flask_sqlalchemy import SQLAlchemy

from notary import Notary


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

    def __init__(self, author, title, text):
        self.author_id = author.id
        self.title = title
        self.text = text
        self.signature = Notary.sign(author.private_key, title, text)

    def __repr__(self):
        return f'<Document #{self.id} by {self.author.username} (author_id={self.author_id})>'
