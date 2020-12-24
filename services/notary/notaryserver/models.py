from flask_sqlalchemy import SQLAlchemy

from cryptography import create_signature, gen_privkey, get_pubkey_from_privkey, verify_signature


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pubkey = db.Column(db.String, nullable=False)
    privkey = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    documents = db.relationship('Document', backref='author', lazy=True)

    def __init__(self, name, phone, address):
        self.name = name
        self.phone = phone
        self.address = address
        self.privkey = gen_privkey()
        self.pubkey = get_pubkey_from_privkey(self.privkey)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def generate_password(self):
        return create_signature(self.privkey, 'user', self.name)

    def verify_password(self, password):
        return verify_signature(self.pubkey, 'user', self.name, password)

    def __repr__(self):
        return f'<User {self.name} (id={self.id})>'


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
        self.signature = create_signature(author.privkey, title, text)

    def __repr__(self):
        return f'<Document #{self.id} by {self.author.name} (author_id={self.author_id})>'
