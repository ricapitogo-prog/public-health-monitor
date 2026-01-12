import pytest
from datetime import datetime

def test_insert_global_stats(test_db, sample_global_data):
    """Test inserting global statistics"""
    success = test_db.insert_global_stats(sample_global_data)
    assert success is True
    
    recent = test_db.get_recent_global_data(hours=24)
    assert len(recent) == 1
    assert recent[0]['total_cases'] == 700000000

def test_insert_country_stats(test_db, sample_country_data):
    """Test inserting country statistics"""
    success = test_db.insert_country_stats(sample_country_data)
    assert success is True
    
    trend = test_db.get_country_trend('USA', days=1)
    assert len(trend) == 1
    assert trend[0]['total_cases'] == 100000000

def test_log_error(test_db):
    """Test error logging"""
    test_db.log_error('TEST_ERROR', 'This is a test error')
    # If no exception, test passes
    assert True

def test_get_recent_global_data_empty(test_db):
    """Test getting data from empty database"""
    recent = test_db.get_recent_global_data(hours=24)
    assert recent == []

def test_data_quality_metrics(test_db, sample_global_data):
    """Test data quality metrics calculation"""
    test_db.insert_global_stats(sample_global_data)
    
    metrics = test_db.get_data_quality_metrics(hours=1)
    assert metrics['actual_data_points'] == 1
    assert metrics['success_rate_percent'] > 0