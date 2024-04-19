from datetime import timedelta, datetime
from fastapi import FastAPI
import requests
import json

from frcm.datamodel.model import FireRiskPrediction, Location, WeatherData, Observations, Forecast
from frcm.data_harvesting.client import WeatherDataClient
import frcm.FRC_service.compute
from frcm.data_harvesting.client_met import METClient
from frcm.data_harvesting.extractor_met import METExtractor
from frcm.database.firestore import save_data_to_db, get_date_weatherdata

class FireRiskAPI:

    def __init__(self, client: WeatherDataClient):
        self.client = client
        self.timedelta_ok = timedelta(days=1) # TODO: when during a day is observations updated? (12:00 and 06:00)
        # TODO (NOTE): Short term forecast updates every 3rd hour with long term forecast every 12th hour at 12:00 and 06:00
        self.interpolate_distance = 720

    def compute(self, wd: WeatherData) -> FireRiskPrediction:
        return frcm.FRC_service.compute.compute(wd)
    
    def fetch_and_compute(self, location, start, end, manage_db=False):
        """Fetch observations and forecast, create WeatherData, and compute prediction."""
        time_now = datetime.now()
        formatted_start_time = start.strftime('%d-%m-%Y')
        formatted_time_now = end.strftime('%d-%m-%Y')
        date_range = f'{formatted_start_time} - {formatted_time_now}'

        if manage_db:
            observations = self.manage_observations(location, date_range, start, end)
        else:
            observations = self.client.fetch_observations(location, start=start, end=end)

        forecast = self.client.fetch_forecast(location, start, end)
        wd = WeatherData(created=time_now, observations=observations, forecast=forecast)
        return self.compute(wd)
    
    def manage_observations(self, location, date_range, start, end):
        """Manage fetching or retrieving observations from database or API."""
        db_observations = get_date_weatherdata(date_range)
        if db_observations:
            print("Using data retrieved from the database.")
            return db_observations
        else:
            observations = self.client.fetch_observations(location, start=start, end=end)
            save_data_to_db(observations.location, date_range, observations.data, observations.source)
            print("No existing data found. Fetched new data and saved to database.")
            return observations
        
    def compute_previous_days(self, location: Location, delta: timedelta):
        time_now = datetime.now()
        start_time = time_now - delta
        return self.fetch_and_compute(location, start_time, time_now, manage_db=True)

    def compute_upcoming_days(self, location: Location, delta: timedelta):
        time_now = datetime.now()
        end_time = time_now + delta
        return self.fetch_and_compute(location, time_now, end_time)

    def compute_specific_period(self, location: Location, start: datetime, end: datetime):
        return self.fetch_and_compute(location, start, end)

    def compute_after_start_date(self, location: Location, start: datetime, delta: timedelta):
        end = start + delta
        return self.fetch_and_compute(location, start, end)

    def compute_before_end_date(self, location: Location, end: datetime, delta: timedelta):
        start = end - delta
        return self.fetch_and_compute(location, start, end)


met_extractor = METExtractor()
# TODO: maybe embed extractor into client
met_client = METClient(extractor=met_extractor)
frc = FireRiskAPI(client=met_client)

app = FastAPI()
@app.get("/api/v1/fireriskPreviousDays")
def fire_risk_previous_days(days: int, longitude: float, latitude: float):
    time_delta = timedelta(days=days)
    location1 = Location(longitude=float(longitude), latitude=float(latitude))
    result = frc.compute_previous_days(location=location1, delta=time_delta)
    return result

@app.get("/api/v1/fireriskSpecificPeriod")
def fire_risk_specific_period(start_date: str, end_date: str, longitude: float, latitude: float):
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    location1 = Location(longitude=float(longitude), latitude=float(latitude))
    result = frc.compute_specific_period(location=location1, start=start, end=end)
    return result


@app.get("/api/v1/fireriskUpcomingDays")
def fire_risk_upcoming_days(days: int, longitude: float, latitude: float):
    delta = timedelta(days=days)
    location1 = Location(longitude=float(longitude), latitude=float(latitude))
    result = frc.compute_upcoming_days(location=location1, delta=delta)
    return result

@app.get("/api/v1/fireriskBeforeEndDate")
def fire_risk_compute_before_end_date(end_date, days, longitude, latitude):
    delta = timedelta(days=int(days))
    location = Location(longitude=longitude, latitude=latitude)
    end = datetime.fromisoformat(end_date)
    result = frc.compute_before_end_date(location, end, delta)
    return result


@app.get("/api/v1/fireriskAfterStartDate")
def fire_risk_compute_before_end_date(start_date, days, longitude, latitude):
    delta = timedelta(days=int(days))
    location = Location(longitude=longitude, latitude=latitude)
    start = datetime.fromisoformat(start_date)
    result = frc.compute_after_start_date(location, start, delta)
    return result


#    delta = timedelta(days=days)
#    location = Location(longitude=longitude, latitude=latitude)
#    start = datetime.fromisoformat(start_date)