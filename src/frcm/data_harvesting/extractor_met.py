import json
import dateutil.parser
import numpy as np
from datetime import datetime, timedelta, timezone
from frcm.data_harvesting.extractor import Extractor
from frcm.datamodel.model import *


class METExtractor(Extractor):

    def extract_observations(self, frost_response_str: str, location: Location, start_time: datetime.datetime, end_time: datetime.datetime) -> Observations:

        source_id = None
        weatherdatapoints = list()
        if start_time > datetime.datetime.now():
            return Observations(source="", location=location,data=weatherdatapoints)


        frost_response = json.loads(frost_response_str)
       
        data_list = frost_response['data']


        if len(data_list) > 1:

            source_id = data_list[0]['sourceId']

            for data in data_list:

                reference_time = dateutil.parser.parse(data['referenceTime'])
                station_observations = data['observations']

                temperature = np.nan
                relative_humidity = np.nan
                wind_speed = np.nan

                for station_observation in station_observations:

                    # string to datatime object required
                    timestamp = reference_time # assume that observations have the same time stamp

                    # TODO: rewrite to use a switch
                    if station_observation['elementId'] == 'air_temperature':
                        temperature = station_observation['value']
                    elif station_observation['elementId'] == 'relative_humidity':
                        relative_humidity = station_observation['value']
                    elif station_observation['elementId'] == 'wind_speed':
                        wind_speed = station_observation['value']

                wd_point = WeatherDataPoint(temperature=temperature,
                                            humidity=relative_humidity,
                                            wind_speed=wind_speed,
                                            timestamp=timestamp
                                            )

                weatherdatapoints.append(wd_point)

        # TODO: maybe also source as part of the parameters - or extract weather data function instead
        observations = Observations(source=source_id, location=location,data=weatherdatapoints)

        return observations

    def extract_forecast(self, met_response_str: str, start_time: datetime.datetime, end_time: datetime.datetime) -> Forecast:

        met_response = json.loads(met_response_str)

        coordinates = met_response['geometry']['coordinates']

        latitude = coordinates[1]
        longitude = coordinates[0]

        location = Location(latitude=latitude, longitude=longitude)

        timeseries = met_response['properties']['timeseries']

        weatherdatapoints = list()

        for forecast in timeseries:

            timestamp = dateutil.parser.parse(forecast['time'])
            string_time = str(timestamp)[:10]
            action = str(timestamp)[19]
            tidssone = str(timestamp)[20:22]
            ny_tid = datetime.datetime(year=int(string_time[:4]), month=int(string_time[5:7]), day=int(string_time[8:10]))
            if action == '+':
                ny_tid = ny_tid + timedelta(hours=int(tidssone))
            if action == '-':
                ny_tid = ny_tid - timedelta(hours=int(tidssone))
            #print(ny_tid)
            if ny_tid > (start_time-timedelta(days=1)):
                if ny_tid > end_time:
                    break

                details = forecast['data']['instant']['details']

                temperature = details['air_temperature']
                humidity = details['relative_humidity']
                wind_speed = details['wind_speed']

                wd_point = WeatherDataPoint(temperature=temperature,
                                        humidity=humidity,
                                        wind_speed=wind_speed,
                                        timestamp=timestamp)

                weatherdatapoints.append(wd_point)

        forecast = Forecast(location=location,data=weatherdatapoints)

        return forecast

    def extract_weatherdata(self, frost_response: str, met_response: str, location: Location, start_time: datetime.datetime, end_time: datetime.datetime) -> WeatherData:

        observations = self.extract_observations(frost_response, location, start_time, end_time)

        forecast = self.extract_forecast(met_response, start_time, end_time)


        now = datetime.datetime.now()  # FIXME: date from each response should be used

        weather_data = WeatherData(created=now,
                                   observations=observations,
                                   forecast=forecast)

        return weather_data
