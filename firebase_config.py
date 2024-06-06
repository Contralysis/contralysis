import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json

# Initialize Firebase
def init_firebase():
    creds_dict = {
        "type": "service_account",
        "project_id": "contralysis-ef9d6",
        "private_key_id": os.getenv('PRIVATE_KEY_ID'),
        "private_key": os.getenv('PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": os.getenv('CLIENT_EMAIL'),
        "client_id": os.getenv('CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL'),
        "universe_domain": "googleapis.com"
    }

    # cred = credentials.Certificate('credentials/contralysis-ef9d6-firebase-adminsdk-cztmd-b5d5a53043.json')
    print(creds_dict)

    cred = credentials.Certificate(creds_dict)
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