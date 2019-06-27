import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from random import shuffle

class Db:
    def __init__(self, cred_path):
        # Use cert for admin
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def save_quote(self, chat_id, text, username):
        chat_ref = self.db.document(f'chats/{str(chat_id)}')
        chat_ref.collection('msgs').add({ 'msg': text, 'user': username })

    def rand_quote(self, chat_id):
        # Returns a generator object
        msgs = self.db.collection(f'chats/{str(chat_id)}/msgs').stream()
        msgs = list(map(lambda doc: doc.to_dict(), msgs))

        if not msgs:
            return None

        shuffle(msgs)
        return msgs[0]

