#!/usr/bin/env python3

from app import app
from models import db, Document, User


with app.app_context():
    db.create_all()
