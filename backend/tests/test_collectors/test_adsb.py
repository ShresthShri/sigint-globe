from app.collectors.adsb import ADSBCollector, INTERFERENCE_THRESHOLD
from tests.conftest import SAMPLE_ADSB_RESPONSE


def test_parse_response_counts():
    collector = ADSBCollector()
    snapshot, observations = collector._parse_response(
        "eastern_med", SAMPLE_ADSB_RESPONSE["ac"]
    )
    assert snapshot.aircraft_total == 6
    assert len(observations) == 6


def test_parse_response_nacp_tracking():
    collector = ADSBCollector()
    snapshot, observations = collector._parse_response(
        "eastern_med", SAMPLE_ADSB_RESPONSE["ac"]
    )
    assert snapshot.aircraft_with_nacp == 6
    assert snapshot.aircraft_low_nacp == 2


def test_parse_spoofed_aircraft():
    collector = ADSBCollector()
    _, observations = collector._parse_response(
        "eastern_med", SAMPLE_ADSB_RESPONSE["ac"]
    )
    spoofed = [o for o in observations if o.hex == "7105a5"]
    assert len(spoofed) == 1
    ac = spoofed[0]
    assert ac.nac_p == 0
    assert ac.nic == 0
    assert ac.rc == 0
    assert ac.flight == "KNE555"
    assert ac.gs == 155.3
    assert ac.tas == 450


def test_parse_military_flag():
    collector = ADSBCollector()
    _, observations = collector._parse_response(
        "eastern_med", SAMPLE_ADSB_RESPONSE["ac"]
    )
    mil = [o for o in observations if o.hex == "ae1234"]
    assert len(mil) == 1
    assert mil[0].is_military is True
    civ = [o for o in observations if o.hex == "7448a4"]
    assert civ[0].is_military is False


def test_parse_skips_no_position():
    collector = ADSBCollector()
    _, observations = collector._parse_response(
        "eastern_med", SAMPLE_ADSB_RESPONSE["ac"]
    )
    no_pos = [o for o in observations if o.hex == "abcdef"]
    assert len(no_pos) == 0


def test_parse_flight_strip():
    collector = ADSBCollector()
    _, observations = collector._parse_response(
        "eastern_med", SAMPLE_ADSB_RESPONSE["ac"]
    )
    rja = [o for o in observations if o.hex == "7448a4"]
    assert rja[0].flight == "RJA153"
