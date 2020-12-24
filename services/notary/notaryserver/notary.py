#!/usr/bin/env python3

import base64

import libnotary


def serialize_bytes(bs):
    return base64.b64encode(bs).decode('utf-8')


def deserialize_bytes(string):
    try:
        return base64.b64decode(string)
    except ValueError as err:
        raise ValueError('Failed to deserialize bytes') from err


def pack_document(title, text):
    return title + '|' + text.replace('|', '\\|')


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
    def sign(private_key, title, text):
        document = pack_document(title, text)
        
        signature = libnotary.sign(
            deserialize_bytes(private_key),
            document.encode('utf-8'))
        
        if signature is None:
            raise ValueError('Invalid private key')
        
        return serialize_bytes(signature)

    @staticmethod
    def verify(public_key, title, text, signature):
        try:
            public_key = deserialize_bytes(public_key)
            signature = deserialize_bytes(signature)
        except ValueError:
            return False  # Garbage input
        
        document = pack_document(title, text)
        result = libnotary.verify(
            public_key, 
            document.encode('utf-8'), 
            signature)
        
        if result is None:
            return False  # The public key is invalid, makes sense to return False
        
        return result
