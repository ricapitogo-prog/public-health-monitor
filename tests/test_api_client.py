import pytest
import responses
from src.api_client import HealthDataAPIClient
from config import BASE_URL

@responses.activate
def test_fetch_global_data_success(sample_global_data):
    """Test successful global data fetch"""
    responses.add(
        responses.GET,
        f"{BASE_URL}/all",
        json=sample_global_data,
        status=200
    )
    
    client = HealthDataAPIClient()
    data = client.fetch_global_data()
    
    assert data is not None
    assert data['cases'] == 700000000
    assert data['deaths'] == 7000000

@responses.activate
def test_fetch_country_data_success(sample_country_data):
    """Test successful country data fetch"""
    responses.add(
        responses.GET,
        f"{BASE_URL}/countries/USA",
        json=sample_country_data,
        status=200
    )
    
    client = HealthDataAPIClient()
    data = client.fetch_country_data('USA')
    
    assert data is not None
    assert data['country'] == 'USA'
    assert data['population'] == 331000000

@responses.activate
def test_fetch_country_data_not_found():
    """Test handling of invalid country"""
    responses.add(
        responses.GET,
        f"{BASE_URL}/countries/InvalidCountry",
        json={'message': 'Country not found'},
        status=404
    )
    
    client = HealthDataAPIClient()
    data = client.fetch_country_data('InvalidCountry')
    
    assert data is None