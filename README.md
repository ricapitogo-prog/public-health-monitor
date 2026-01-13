# Public Health Data Monitor

A production-ready COVID-19 monitoring system demonstrating real-time data engineering best practices with disease.sh API.

## Problem Statement

Public health agencies need reliable real-time data to track disease outbreaks. This system provides:
- **Automated monitoring**: Collect data every 10 minutes
- **Data validation**: Detect API schema changes and anomalies
- **Surge detection**: Alert when daily cases increase >5%
- **Historical tracking**: Store all data for trend analysis


## Architecture
```
┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│  disease.sh  │────▶│   Validator  │────▶│   SQLite    │
│     API      │     │  (Pydantic)  │     │  Database   │
└──────────────┘     └──────────────┘     └─────────────┘
       │                    │                     │
       │                    │                     │
       ▼                    ▼                     ▼
  Retry Logic       Schema Validation      Error Logging
  Rate Handling     Range Checking         Surge Detection
```

## Quick Start

### Installation
```bash
# Clone and setup
git clone <your-repo>
cd public_health_monitor
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running
```bash
# Start data collection (runs indefinitely)
python main.py

# In another terminal, start health check API
python health_check.py

# Check system status
curl http://localhost:5000/health
curl http://localhost:5000/alerts
curl http://localhost:5000/summary
```

## Testing
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

**Test Coverage**: 85%+

## What This Demonstrates

### Production-Ready Features
✅ Real-time API integration (disease.sh)  
✅ Automatic retry with exponential backoff  
✅ Schema validation with Pydantic  
✅ Comprehensive error handling  
✅ Structured logging  
✅ SQLite storage with analytics  
✅ Health check endpoints  
✅ Surge detection algorithms  
✅ 85%+ test coverage

## Real-World Data Characteristics

The disease.sh API reflects actual COVID-19 reporting patterns as of 2025:
- Many countries now report weekly rather than daily
- `todayCases` often shows 0 due to infrequent updates
- The system correctly captures this real-world scenario

**Production Considerations:**
- In 2020-2021, this data changed rapidly (thousands of cases daily)
- Current data demonstrates the system handles both high-volatility and low-volatility scenarios
- For more active monitoring, the system could be adapted to track:
  - Seasonal influenza (more active reporting)
  - Respiratory syncytial virus (RSV)
  - Wastewater surveillance data
  - Hospital capacity metrics

### Error Handling

| Error Type     | Strategy                                            |
|----------------|-----------------------------------------------------|
| API Timeout    | Retry 3x with exponential backoff                   |
| Rate Limit     | Wait and retry (though disease.sh is very generous) |
| Schema Change  | Log error, preserve raw data                        |
| Invalid Data   | Reject with detailed validation errors              |
| Database Error | Log and continue processing                         |

## Features

**Data Collection:**
- Global COVID-19 statistics
- Country-specific data (5 countries by default)
- Tracks cases, deaths, recoveries, active cases
- Stores population-normalized metrics

**Analytics:**
- Case surge detection (>5% daily increase)
- Data quality metrics (success rate, missing points)
- Top countries by daily cases
- 7-day trends by country

**Monitoring:**
- Health check endpoint
- Alert system for case surges
- Data quality dashboard
- Comprehensive logging

## Design Decisions

### Why disease.sh?
- **Pro**: Free, no API key, generous rate limits, well-maintained
- **Pro**: Real public health data, updated every 10 minutes
- **Con**: Limited to COVID-19/Influenza data
- **Production**: Would add WHO API, CDC data sources

### Why 10-Minute Intervals?
- **Pro**: Matches disease.sh update frequency
- **Pro**: Balances data freshness with API load
- **Con**: Might miss very rapid changes
- **Production**: Could parallelize with multiple data sources

### Why SQLite?
- **Pro**: Zero configuration, perfect for learning
- **Pro**: File-based, easy to inspect data
- **Con**: Single-writer limitation
- **Production**: PostgreSQL with TimescaleDB for time-series

### Validation Strategy
- **Choice**: Strict Pydantic validation with custom validators
- **Rationale**: Catch data quality issues immediately
- **Trade-off**: Slight performance overhead worth it for data integrity

## Future Enhancements

With more time, I would add:

1. **Email/SMS Alerts**: Notify when surge detected
2. **Dashboard**: Streamlit app with charts
3. **More Data Sources**: WHO, CDC, state health departments
4. **Predictive Model**: ML model for case forecasting
5. **Docker**: Containerization for deployment
6. **CI/CD**: GitHub Actions for automated testing
7. **API**: REST API for querying historical data

## Project Structure
```
public_health_monitor/
├── src/
│   ├── __init__.py
│   ├── api_client.py          # disease.sh API client with retry logic
│   ├── validator.py           # Pydantic data validation
│   ├── database.py            # SQLite operations & analytics
│   └── logger.py              # Structured logging setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_api_client.py     # API client tests (mocked)
│   ├── test_validator.py      # Validation logic tests
│   └── test_database.py       # Database operation tests
├── logs/                       # Daily log files (generated)
├── htmlcov/                    # Test coverage reports (generated)
├── .gitignore                  # Git exclusions
├── config.py                   # Configuration settings
├── main.py                     # Main data collection pipeline
├── health_check.py             # Flask health monitoring API
├── requirements.txt            # Python dependencies
├── public_health_data.db       # SQLite database (generated)
└── README.md                   # Project documentation
```

## Author

**Rica Mae Pitogo**
- GitHub: [ricapitogo-prog](https://github.com/ricapitogo-prog)
- LinkedIn: [Rica Mae Pitogo](https://www.linkedin.com/in/rica-mae-pitogo-a7aa10193/)

## Acknowledgments

- **disease.sh**: Free public health data API
- **Production framework**: Inspired by [Fit Data Scientist](https://penelopefitdatascientist.substack.com/)

---
