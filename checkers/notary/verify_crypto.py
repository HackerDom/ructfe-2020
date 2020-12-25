class Verify:
    @staticmethod
    def public_key(public_key):
        return True

    @staticmethod
    def private_key(private_key):
        return True

    @staticmethod
    def signature(signature, document_text):
        return True

    @staticmethod
    def user_password(password, username):
        return True

    @staticmethod
    def document_password(password, document_id):
        return True

    @staticmethod
    def key_pair(private_key, public_key):
        return True
