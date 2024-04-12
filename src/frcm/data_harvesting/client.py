import abc
from datetime import datetime
from frcm.datamodel.model import Location, Observations, Forecast


class WeatherDataClient:

    # TODO: add variants for time period on observations and timedelta on forecast

    @abc.abstractmethod
    def fetch_observations(self, location: Location, start: datetime, end: datetime) -> Observations:
        pass

    @abc.abstractmethod
    def fetch_forecast(self, location: Location, start: datetime, end: datetime) -> Forecast:
        pass
