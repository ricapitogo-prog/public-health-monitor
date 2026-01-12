from src.api_client import HealthDataAPIClient
from src.validator import validate_global_data, validate_country_data
from src.database import HealthDatabase
from src.logger import setup_logger
from config import DB_PATH, FETCH_INTERVAL_MINUTES, COUNTRIES
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# Setup logger
logger = setup_logger(__name__)

# Initialize components
api_client = HealthDataAPIClient()
database = HealthDatabase(DB_PATH)

def fetch_and_store_data():
    """Main function that runs every 10 minutes"""
    logger.info("=" * 60)
    logger.info("Starting public health data collection")
    
    # Fetch and store global data
    logger.info("Fetching global statistics...")
    global_data = api_client.fetch_global_data()
    
    if global_data:
        validated = validate_global_data(global_data)
        if validated:
            success = database.insert_global_stats(global_data)
            if success:
                logger.info(f"Global: {validated.cases:,} cases, {validated.todayCases:,} today")
            else:
                logger.error("Failed to store global data")
        else:
            logger.error("Global data validation failed")
            database.log_error('VALIDATION_FAILED', 'Global data invalid', str(global_data))
    else:
        logger.error("Failed to fetch global data")
        database.log_error('API_FETCH_FAILED', 'Could not retrieve global data')
    
    # Fetch and store country data
    logger.info(f"Fetching data for {len(COUNTRIES)} countries...")
    country_data = api_client.fetch_all_countries()
    
    successful = 0
    for data in country_data:
        validated = validate_country_data(data)
        if validated:
            success = database.insert_country_stats(data)
            if success:
                logger.info(f"{data['country']}: {validated.todayCases:,} cases today")
                successful += 1
        else:
            logger.error(f"Validation failed for {data.get('country', 'unknown')}")
            database.log_error('VALIDATION_FAILED', f'Country data invalid', str(data))
    
    logger.info(f"Successfully stored data for {successful}/{len(country_data)} countries")
    logger.info("Data collection cycle complete")

def main():
    """Setup scheduler and run indefinitely"""
    logger.info("Public Health Monitor starting up")
    logger.info(f"Monitoring countries: {', '.join(COUNTRIES)}")
    logger.info(f"Will fetch data every {FETCH_INTERVAL_MINUTES} minutes")
    
    # Run once immediately
    fetch_and_store_data()
    
    # Setup scheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(
        fetch_and_store_data,
        'interval',
        minutes=FETCH_INTERVAL_MINUTES,
        id='health_data_fetch_job'
    )
    
    try:
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")

if __name__ == '__main__':
    main()