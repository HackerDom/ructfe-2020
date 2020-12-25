#!/usr/bin/env python3

import base64
import msgpack

import libnotary


def serialize_bytes(bs):
    return base64.b64encode(bs).decode('utf-8')


def deserialize_bytes(string):
    try:
        return base64.b64decode(string)
    except ValueError as err:
        raise ValueError('Failed to deserialize bytes') from err


def pack_document(title, text):
    document = {
        'title': title,
        'text': text
    }

    return msgpack.dumps(document)


def load_document(document_data):
    try:
        document = msgpack.loads(document_data)
        return document['title'], document['text']
    except (ValueError, KeyError):
        raise ValueError('Failed to load document')


class Notary:
    @staticmethod
    def generate_private_key():
        private_key = libnotary.generate()
        
        if private_key is None:
            raise ValueError('Failed to generate a private key')
        
        return serialize_bytes(private_key)

    @staticmethod
    def get_public_key(private_key):
        public_key = libnotary.get_public(deserialize_bytes(private_key))
        
        if public_key is None:
            raise ValueError('Invalid private key')
        
        return serialize_bytes(public_key)

    @staticmethod
    def sign(private_key, document):
        signature = libnotary.sign(deserialize_bytes(private_key), document)
        
        if signature is None:
            raise ValueError('Invalid private key')
        
        return serialize_bytes(signature)

    @staticmethod
    def verify(public_key, document, signature):
        try:
            public_key = deserialize_bytes(public_key)
            signature = deserialize_bytes(signature)
        except ValueError:
            return False  # Garbage input

        result = libnotary.verify(public_key, document, signature)
        
        if result is None:
            return False  # The public key is invalid, makes sense to return False
        
        return result
