import pytest
from datetime import datetime, timedelta
import random

from database.firestore import save_data, get_date_firerisk, delete_firerisk

@pytest.fixture
def test_data():
    # Generate a unique date string to use as a document ID
    test_date = (datetime.now() + timedelta(days=random.randint(1, 100))).strftime("%Y-%m-%d")
    location = type('Location', (object,), {'latitude': 34.0522, 'longitude': -118.2437})()
    risks = [type('Risk', (object,), {'timestamp': datetime.now(), 'ttf': random.random()})() for _ in range(3)]
    return location, test_date, risks

def test_firerisk_scenario(test_data):
    location, test_date, risks = test_data

    # Step 1: Save data
    save_data(location, test_date, risks)

    # Step 2: Retrieve and check the data
    document = get_date_firerisk(test_date)
    assert document is not None, "Document was not found after saving."
    assert document['latitude'] == location.latitude, "Latitude mismatch."
    assert document['longitude'] == location.longitude, "Longitude mismatch."
    assert len(document['fire_risks']) == len(risks), "Number of risks mismatch."

    # Step 3: Delete the document
    delete_firerisk(test_date)
    document_after_deletion = get_date_firerisk(test_date)
    assert document_after_deletion is None, "Document was not deleted."