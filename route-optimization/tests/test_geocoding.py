import httpx
import pytest

from route_optimization.errors import LocationNotFoundError, OutsideTamilNaduError
from route_optimization.geocoding import geocode_location


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_geocode_tamil_nadu_location():
    def handler(request):
        return httpx.Response(
            200,
            json=[{
                "lat": "12.9165",
                "lon": "79.1325",
                "display_name": "Vellore, Tamil Nadu, India",
                "address": {"state": "Tamil Nadu", "ISO3166-2-lvl4": "IN-TN"},
            }],
        )

    with _client(handler) as client:
        point = geocode_location("Vellore", client)
    assert point.name == "Vellore"
    assert point.latitude == pytest.approx(12.9165)


def test_location_not_found():
    with _client(lambda request: httpx.Response(200, json=[])) as client:
        with pytest.raises(LocationNotFoundError):
            geocode_location("Unknown", client)


def test_outside_tamil_nadu_rejected():
    def handler(request):
        return httpx.Response(
            200,
            json=[{
                "lat": "12.97",
                "lon": "77.59",
                "display_name": "Bengaluru, Karnataka, India",
                "address": {"state": "Karnataka", "ISO3166-2-lvl4": "IN-KA"},
            }],
        )
    with _client(handler) as client:
        with pytest.raises(OutsideTamilNaduError):
            geocode_location("Bengaluru", client)
