import os
import base64
from google.oauth2 import service_account
from google.cloud import firestore
import json
from decouple import config
from datetime import datetime
from frcm.datamodel.model import WeatherDataPoint, Location, WeatherData, Observations, Forecast

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

def save_data_to_db(location, date, risks, src):
    db = get_firestore_db()
    doc_ref = db.collection('weather_data').document(date)
    data = {
        'observation_date': date,
        'source': src,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'weather_points': []
    }
    
    for risk in risks:
        fire_risk_data = {
            'date_time': risk.timestamp.isoformat(),
            'temperature': risk.temperature,
            'humidity': risk.humidity,
            'wind_speed': risk.wind_speed
        }
        data['weather_points'].append(fire_risk_data)
    
    doc_ref.set(data)
    print("Data saved successfully")

def get_date_weatherdata(date):
    db = get_firestore_db()
    doc_ref = db.collection('weather_data').document(date)
    doc = doc_ref.get()
    if doc.exists:
        doc_dict = doc.to_dict()
        location = Location(latitude=doc_dict['latitude'], longitude=doc_dict['longitude'])
        weather_data_points = [WeatherDataPoint(
            temperature=dp['temperature'],
            humidity=dp['humidity'],
            wind_speed=dp['wind_speed'],
            timestamp=datetime.fromisoformat(dp['date_time'])
        ) for dp in doc_dict['weather_points']]
        observations = Observations(source=doc_dict['source'], location=location, data=weather_data_points)
        return observations
    else:
        print("No such document!")
    return None

def delete_firerisk(date):
    """
    Delete weatherdata by datespan
    """
    db = get_firestore_db()
    db.collection('weather_data').document(date).delete()
    print(f"Document {date} successfully deleted.")


