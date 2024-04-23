import os
import base64
from google.oauth2 import service_account
from google.cloud import firestore
import json
from decouple import config
from datetime import datetime
from frcm.datamodel.model import WeatherDataPoint, Location, WeatherData, Observations, Forecast

def get_firestore_client():
    try:
        # Decode the base64-encoded credentials
        credentials_json = base64.b64decode(config('FIREBASE_CREDENTIALS_BASE64')).decode('utf-8')
        
        # Load the credentials from the decoded JSON string
        credentials = service_account.Credentials.from_service_account_info(json.loads(credentials_json))
        
        # Use the credentials to initialize the Firestore client
        return firestore.Client(credentials=credentials, project=credentials.project_id)
    except Exception as e:
        print(f"Failed to initialize Firestore client: {e}")
        return None

# Initialize Firestore database reference
def get_firestore_db():
    try:
        client = get_firestore_client()
        if client is not None:
            return client
        else:
            raise Exception("Failed to get Firestore client")
    except Exception as e:
        print(f"Error getting Firestore database: {e}")
        return None

def save_data_to_db(location, date, risks, src):
    try:
        db = get_firestore_db()
        if db is not None:
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
    except Exception as e:
        print(f"Failed to save data: {e}")

def get_date_weatherdata(date):
    try:
        db = get_firestore_db()
        if db is not None:
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
    except Exception as e:
        print(f"Error fetching data for {date}: {e}")
    return None

def delete_firerisk(date):
    try:
        db = get_firestore_db()
        if db is not None:
            db.collection('weather_data').document(date).delete()
            print(f"Document {date} successfully deleted.")
    except Exception as e:
        print(f"Failed to delete data for {date}: {e}")
