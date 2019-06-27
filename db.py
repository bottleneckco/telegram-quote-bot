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

        # print(grp_id, text, username)

    def rand_quote(self, chat_id):
        # Returns a generator object
        msgs = self.db.collection(f'chats/{str(chat_id)}/msgs').stream()
        msgs = list(map(lambda doc: doc.to_dict(), msgs))

        if not msgs:
            return None

        shuffle(msgs)
        return msgs[0]



        
        


    

# u in front of string is unicode escaped string
# doc_ref = db.collection(u'users').document(u'alovelace')
# doc_ref.set({
#     u'first': u'Ada',
#     u'last': u'Lovelace',
#     u'born': 1815
# })

# doc_ref = db.collection(u'users').document(u'aturing')
# doc_ref.set({
#     u'first': u'Alan',
#     u'middle': u'Mathison',
#     u'last': u'Turing',
#     u'born': 1912
# })

# doc_ref.delete()

# users_ref = db.collection(u'users')
# docs = users_ref.stream()
#
# for doc in docs:
#     print(u'{} => {}'.format(doc.id, doc.to_dict()))

# firestore.transaction
