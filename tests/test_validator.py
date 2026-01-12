import pytest
from src.validator import validate_global_data, validate_country_data

def test_validate_good_global_data(sample_global_data):
    """Test validation of correct global data"""
    result = validate_global_data(sample_global_data)
    
    assert result is not None
    assert result.cases == 700000000
    assert result.deaths == 7000000

def test_validate_deaths_exceed_cases(sample_global_data):
    """Test validation fails when deaths > cases"""
    bad_data = sample_global_data.copy()
    bad_data['deaths'] = 800000000  # More than cases
    
    result = validate_global_data(bad_data)
    assert result is None

def test_validate_negative_cases(sample_global_data):
    """Test validation fails for negative cases"""
    bad_data = sample_global_data.copy()
    bad_data['cases'] = -100
    
    result = validate_global_data(bad_data)
    assert result is None

def test_validate_good_country_data(sample_country_data):
    """Test validation of correct country data"""
    result = validate_country_data(sample_country_data)
    
    assert result is not None
    assert result.country == 'USA'
    assert result.population == 331000000

def test_validate_missing_country_name(sample_country_data):
    """Test validation fails without country name"""
    bad_data = sample_country_data.copy()
    del bad_data['country']
    
    result = validate_country_data(bad_data)
    assert result is None