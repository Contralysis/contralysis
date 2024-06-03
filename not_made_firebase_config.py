import firebase_admin
from firebase_admin import credentials, auth, firestore

def init_firebase():
    cred = credentials.Certificate('path_to_your_firebase_service_account.json')
    firebase_admin.initialize_app(cred)
    return firebase_admin

def get_user_reports(user_id, address=None):
    db = firestore.client()
    if address:
        docs = db.collection('reports').where('user_id', '==', user_id).where('address', '==', address).stream()
    else:
        docs = db.collection('reports').where('user_id', '==', user_id).stream()
    
    reports = []
    for doc in docs:
        reports.append(doc.to_dict())
    return reports

def save_report(user_id, address, report):
    db = firestore.client()
    db.collection('reports').add({
        'user_id': user_id,
        'address': address,
        'report': report
    })
