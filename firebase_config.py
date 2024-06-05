import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Firebase
def init_firebase():
    cred = credentials.Certificate('credentials/contralysis-ef9d6-firebase-adminsdk-cztmd-b5d5a53043.json')
    firebase_admin.initialize_app(cred)

def save_report(user_id, address, result, analysis):
    db = firestore.client()

    db.collection('results').add({
        'user_id': user_id,
        'address': address,
        'result': result,
        'analysis': analysis
    })

def get_report(user_id, address):
    db = firestore.client()

    docs = db.collection('results').where('user_id', '==', user_id).where('address', '==', address).stream()

    for doc in docs:
        return doc.to_dict().get('result')
    
    return None

def get_user_reports(user_id):
    db = firestore.client()
    docs = db.collection('results').where('user_id', '==', user_id).stream()

    reports = [doc.to_dict() for doc in docs]

    return reports

def get_analysis(user_id, address):
    db = firestore.client()

    docs = db.collection('results').where('user_id', '==', user_id).where('address', '==', address).stream()

    for doc in docs:
        return doc.to_dict().get('analysis')
    
    return None

def verify_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        
        return decoded_token['uid']
    
    except Exception as e:
        return None