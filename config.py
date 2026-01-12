# API Configuration
BASE_URL = 'https://disease.sh/v3/covid-19'

# Countries to monitor (can add more)
COUNTRIES = ['USA', 'UK', 'Canada', 'Germany', 'Japan']

# Database Configuration
DB_PATH = 'public_health_data.db'

# Scheduling Configuration
FETCH_INTERVAL_MINUTES = 10  # disease.sh updates every 10 minutes

# Alert thresholds
CASE_INCREASE_THRESHOLD_PERCENT = 5  # Alert if daily cases increase >5%