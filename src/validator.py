from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class GlobalHealthData(BaseModel):
    """Validates global health statistics"""
    
    updated: int = Field(..., description="Unix timestamp in milliseconds")
    cases: int = Field(..., ge=0, description="Total cases")
    deaths: int = Field(..., ge=0, description="Total deaths")
    recovered: int = Field(..., ge=0, description="Total recovered")
    active: int = Field(..., ge=0, description="Active cases")
    critical: Optional[int] = Field(None, ge=0)
    todayCases: Optional[int] = Field(None, ge=0)
    todayDeaths: Optional[int] = Field(None, ge=0)
    
    @validator('deaths')
    def deaths_not_greater_than_cases(cls, v, values):
        """Deaths can't exceed total cases"""
        if 'cases' in values and v > values['cases']:
            raise ValueError(f'Deaths ({v}) cannot exceed cases ({values["cases"]})')
        return v
    
    @validator('recovered')
    def recovered_reasonable(cls, v, values):
        """Recovered should be reasonable compared to total cases"""
        if 'cases' in values and v > values['cases']:
            raise ValueError(f'Recovered ({v}) cannot exceed cases ({values["cases"]})')
        return v
    
    @validator('active')
    def active_cases_reasonable(cls, v, values):
        """Active cases should roughly equal cases - deaths - recovered"""
        if 'cases' in values and 'deaths' in values and 'recovered' in values:
            expected_active = values['cases'] - values['deaths'] - values['recovered']
            # Allow 10% margin due to data reporting delays
            if abs(v - expected_active) > values['cases'] * 0.1:
                raise ValueError(f'Active cases ({v}) inconsistent with totals')
        return v

class CountryHealthData(BaseModel):
    """Validates country-specific health statistics"""
    
    updated: int
    country: str = Field(..., min_length=2)
    cases: int = Field(..., ge=0)
    deaths: int = Field(..., ge=0)
    recovered: int = Field(..., ge=0)
    active: int = Field(..., ge=0)
    critical: Optional[int] = Field(None, ge=0)
    todayCases: Optional[int] = Field(None, ge=0)
    todayDeaths: Optional[int] = Field(None, ge=0)
    population: Optional[int] = Field(None, ge=0)
    tests: Optional[int] = Field(None, ge=0)
    casesPerOneMillion: Optional[float] = Field(None, ge=0)
    deathsPerOneMillion: Optional[float] = Field(None, ge=0)
    
    @validator('todayCases')
    def today_cases_reasonable(cls, v, values):
        """Today's cases shouldn't exceed 1% of population"""
        if v is not None and 'population' in values and values['population']:
            if v > values['population'] * 0.01:
                raise ValueError(f'Today\'s cases ({v}) seems unreasonably high')
        return v
    
    @validator('casesPerOneMillion')
    def cases_per_million_matches(cls, v, values):
        """Verify cases per million calculation"""
        if v is not None and 'cases' in values and 'population' in values:
            if values['population'] > 0:
                expected = (values['cases'] / values['population']) * 1000000
                # Allow 5% margin for rounding
                if abs(v - expected) > expected * 0.05:
                    raise ValueError(f'Cases per million ({v}) doesn\'t match calculation')
        return v

def validate_global_data(api_data: dict) -> Optional[GlobalHealthData]:
    """
    Validate global API response
    Returns: GlobalHealthData object if valid, None if invalid
    """
    try:
        validated = GlobalHealthData(**api_data)
        return validated
        
    except ValueError as e:
        print(f"ERROR: Validation failed: {e}")
        return None
        
    except Exception as e:
        print(f"ERROR: Unexpected validation error: {e}")
        return None

def validate_country_data(api_data: dict) -> Optional[CountryHealthData]:
    """
    Validate country API response
    Returns: CountryHealthData object if valid, None if invalid
    """
    try:
        validated = CountryHealthData(**api_data)
        return validated
        
    except ValueError as e:
        print(f"ERROR: Validation failed for {api_data.get('country', 'unknown')}: {e}")
        return None
        
    except Exception as e:
        print(f"ERROR: Unexpected validation error: {e}")
        return None

# Test it
if __name__ == '__main__':
    # Test valid global data
    valid_global = {
        'updated': int(datetime.now().timestamp() * 1000),
        'cases': 700000000,
        'deaths': 7000000,
        'recovered': 675000000,
        'active': 18000000,
        'critical': 50000,
        'todayCases': 50000,
        'todayDeaths': 500
    }
    
    result = validate_global_data(valid_global)
    if result:
        print("✓ Valid global data passed validation")
        print(f"  Total cases: {result.cases:,}")
    
    # Test invalid data (deaths > cases)
    invalid_global = valid_global.copy()
    invalid_global['deaths'] = 800000000  # More deaths than cases!
    
    result = validate_global_data(invalid_global)
    if result is None:
        print("✓ Invalid data correctly rejected")