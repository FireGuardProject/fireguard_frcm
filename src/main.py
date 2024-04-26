import datetime

from frcm.logic.bus_logic import FireRiskAPI
from frcm.data_harvesting.client_met import METClient
from frcm.data_harvesting.extractor_met import METExtractor
from frcm.datamodel.model import Location

# sample code illustrating how to use the Fire Risk Computation API (FRCAPI)
if __name__ == "__main__":

    met_extractor = METExtractor()

    # TODO: maybe embed extractor into client
    met_client = METClient(extractor=met_extractor)

    frc = FireRiskAPI(client=met_client)

    locationA = Location(latitude=60.383, longitude=5.3327)  # Bergen
    locationB = Location(latitude=59.4136, longitude=5.2680)  # Haugesund

    delta = datetime.timedelta(days=3)

    predictions = frc.compute_previous_days(locationB, delta)

    # predictions = frc.compute_specific_period(location, datetime.datetime.now() - delta, datetime.datetime.now() + delta)

    print(predictions)
