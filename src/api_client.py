import requests
import time
from typing import Optional, Dict, List
from config import BASE_URL, COUNTRIES

class HealthDataAPIClient:
    """Handles all interactions with disease.sh API"""
    
    def __init__(self, max_retries: int = 3):
        self.base_url = BASE_URL
        self.countries = COUNTRIES
        self.max_retries = max_retries

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """
        Make API request with retry logic
        Args:
            endpoint: Full URL to request
        Returns: JSON response or None
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(endpoint, timeout=10)
                
                # Check for rate limiting (though disease.sh is very generous)
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.HTTPError as e:
                # Don't retry on client errors (4xx)
                if 400 <= response.status_code < 500:
                    print(f"Client error: {e}")
                    return None
                # Retry on server errors (5xx)
                print(f"Server error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        print(f"All {self.max_retries} attempts failed")
        return None

    def fetch_global_data(self) -> Optional[Dict]:
        """Fetch global COVID-19 statistics with retry"""
        endpoint = f"{self.base_url}/all"
        return self._make_request(endpoint)

    def fetch_country_data(self, country: str) -> Optional[Dict]:
        """Fetch data for a specific country with retry"""
        endpoint = f"{self.base_url}/countries/{country}"
        return self._make_request(endpoint)
    
    def fetch_all_countries(self) -> List[Dict]:
        """
        Fetch data for all monitored countries
        Returns: List of dictionaries with country data
        """
        results = []
        for country in self.countries:
            data = self.fetch_country_data(country)
            if data:
                results.append(data)
            time.sleep(0.5)  # Be nice to the API
        return results
    
    def fetch_historical_data(self, country: str, days: int = 30) -> Optional[Dict]:
        """
        Fetch historical data for a country
        Args:
            country: Country name
            days: Number of days of history (max 30 for free tier)
        Returns: Dictionary with historical data
        """
        endpoint = f"{self.base_url}/historical/{country}?lastdays={days}"
        
        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to fetch historical data: {e}")
            return None

# Test it works
if __name__ == '__main__':
    client = HealthDataAPIClient()
    
    # Test global data
    print("Fetching global data...")
    global_data = client.fetch_global_data()
    if global_data:
        print("✓ Global Data:")
        print(f"  Total Cases: {global_data['cases']:,}")
        print(f"  Total Deaths: {global_data['deaths']:,}")
        print(f"  Total Recovered: {global_data['recovered']:,}")
        print(f"  Active Cases: {global_data['active']:,}")
    
    # Test country data
    print("\nFetching USA data...")
    usa_data = client.fetch_country_data('USA')
    if usa_data:
        print("✓ USA Data:")
        print(f"  Today's Cases: {usa_data['todayCases']:,}")
        print(f"  Today's Deaths: {usa_data['todayDeaths']:,}")
        print(f"  Population: {usa_data['population']:,}")