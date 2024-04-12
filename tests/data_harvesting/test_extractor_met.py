import os
import datetime
import sys

import unittest
import json

from frcm.data_harvesting.extractor_met import METExtractor

import tests.sampledata.met_sample_forecast as sampledata_met
import tests.sampledata.frost_sample_observation as sampledata_frost

#current = os.path.dirname(os.path.realpath(__file__))
#parent = os.path.dirname(current)
#sys.path.append(parent)

from frcm.datamodel.model import Location


class TestUtil(unittest.TestCase):

    def setUp(self):

        self.location_obs = Location(latitude=60.383, longitude=5.3327)
        self.location_fct = Location(latitude=60.3915, longitude=5.3199)

        self.start_time = datetime.datetime(year=2023, month=9, day=17)
        self.end_time = datetime.datetime(year=2023, month=9, day=21)

        self.met_extractor = METExtractor()

        self.met_sample_forecast_str = json.dumps(sampledata_met.met_sample_forecast)
        self.frost_sample_observation_str = json.dumps(sampledata_frost.frost_sample_observation)

    def test_extractor_obs(self):

        observations = self.met_extractor.extract_observations(self.frost_sample_observation_str,
                                                               self.location_obs, self.start_time, self.end_time)
        print(observations)

        self.assertEqual(len(observations.data), 24)

    def test_extractor_fct(self):

        forecast = self.met_extractor.extract_forecast(self.met_sample_forecast_str, self.start_time, self.end_time)

        print(forecast)

        self.assertEqual(len(forecast.data), 61)

    def test_extractor_weatherdata(self):

        weatherdata = self.met_extractor.extract_weatherdata(frost_response=self.frost_sample_observation_str,
                                                             met_response=self.met_sample_forecast_str,
                                                             location=self.location_obs,
                                                             start_time=self.start_time, end_time=self.end_time)

        self.assertEqual(self.location_obs, weatherdata.observations.location)
        self.assertEqual(self.location_fct, weatherdata.forecast.location)

        self.assertEqual(len(weatherdata.observations.data), 24)
        self.assertEqual(len(weatherdata.forecast.data), 61)

if __name__ == '__main__':
    unittest.main()




