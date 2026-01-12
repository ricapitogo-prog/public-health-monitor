import pytest
import os
from src.database import HealthDatabase
from datetime import datetime

@pytest.fixture
def test_db():
    """Create a temporary test database"""
    test_db_path = 'test_health.db'
    db = HealthDatabase(test_db_path)
    yield db
    # Cleanup after test
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.fixture
def sample_global_data():
    """Sample global API response with current timestamp"""
    # Use current time in milliseconds (as the API does)
    current_time_ms = int(datetime.now().timestamp() * 1000)
    return {
        'updated': current_time_ms,
        'cases': 700000000,
        'deaths': 7000000,
        'recovered': 675000000,
        'active': 18000000,
        'critical': 50000,
        'todayCases': 50000,
        'todayDeaths': 500
    }

@pytest.fixture
def sample_country_data():
    """Sample country API response with current timestamp"""
    # Use current time in milliseconds (as the API does)
    current_time_ms = int(datetime.now().timestamp() * 1000)
    return {
        'updated': current_time_ms,
        'country': 'USA',
        'cases': 100000000,
        'deaths': 1000000,
        'recovered': 97000000,
        'active': 2000000,
        'critical': 10000,
        'todayCases': 50000,
        'todayDeaths': 500,
        'population': 331000000,
        'tests': 500000000,
        'casesPerOneMillion': 302115,
        'deathsPerOneMillion': 3021
    }