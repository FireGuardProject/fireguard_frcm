import os
import base64
from google.oauth2 import service_account
from google.cloud import firestore
import json
from decouple import config

def get_firestore_client():
    # Decode the base64-encoded credentials
    credentials_json = base64.b64decode(config('FIREBASE_CREDENTIALS_BASE64')).decode('utf-8')
    
    # Load the credentials from the decoded JSON string
    credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
    
    # Use the credentials to initialize the Firestore client
    return firestore.Client(credentials=credentials, project=credentials.project_id)

# Initialize Firestore database reference
def get_firestore_db():
    client = get_firestore_client()
    return client

def save_data(location, date, risks):
    db = get_firestore_db()
    doc_ref = db.collection('fire_risks').document(date)
    data = {
        'observation_date': date,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'fire_risks': []
    }
    
    for risk in risks:
        fire_risk_data = {
            'date_time': risk.timestamp.isoformat(),
            'risk_value': risk.ttf
        }
        data['fire_risks'].append(fire_risk_data)
    
    doc_ref.set(data)
    print("Data saved successfully to Firestore!")

def get_date_firerisk(date):
    """
    Retrieve a single firerisk
    """
    db = get_firestore_db()
    doc_ref = db.collection('fire_risks').document(date)
    doc = doc_ref.get()
    if doc.exists:
        print(f"Document data: {doc.to_dict()}")
        return doc.to_dict()
    else:
        print("No such document!")
    return None

def get_all_firerisks():
    """
    Retrieve all firerisk
    """
    db = get_firestore_db()
    docs = db.collection('fire_risks').stream()
    for doc in docs:
        print(f"{doc.id} => {doc.to_dict()}")
    return [doc.to_dict() for doc in docs]

def delete_firerisk(date):
    """
    Delete a specific firerisk
    """
    db = get_firestore_db()
    db.collection('fire_risks').document(date).delete()
    print(f"Document {date} successfully deleted.")


