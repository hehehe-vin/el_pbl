from google.cloud import firestore

db = firestore.Client()

def col_ref(name):
    return db.collection(name)

def doc_ref(collection, doc_id):
    return db.collection(collection).document(doc_id)

def get_doc(collection, doc_id):
    return doc_ref(collection, doc_id).get()

def set_doc(collection, doc_id, data):
    return doc_ref(collection, doc_id).set(data)

def update_doc(collection, doc_id, data):
    return doc_ref(collection, doc_id).update(data)

def delete_doc(collection, doc_id):
    return doc_ref(collection, doc_id).delete()

def add_to_collection(collection, data):
    return col_ref(collection).add(data)
