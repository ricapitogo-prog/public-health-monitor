import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class HealthDatabase:
    """Manages SQLite database for public health data"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Global statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                total_cases INTEGER NOT NULL,
                total_deaths INTEGER NOT NULL,
                total_recovered INTEGER NOT NULL,
                active_cases INTEGER NOT NULL,
                critical_cases INTEGER,
                today_cases INTEGER,
                today_deaths INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Country-specific data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS country_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                country TEXT NOT NULL,
                total_cases INTEGER NOT NULL,
                total_deaths INTEGER NOT NULL,
                total_recovered INTEGER NOT NULL,
                active_cases INTEGER NOT NULL,
                critical_cases INTEGER,
                today_cases INTEGER,
                today_deaths INTEGER,
                population INTEGER,
                tests INTEGER,
                cases_per_million REAL,
                deaths_per_million REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Error log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                raw_response TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_global_stats(self, data: Dict) -> bool:
        """Insert global statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.fromtimestamp(data['updated'] / 1000)  # Convert ms to seconds
            
            cursor.execute('''
                INSERT INTO global_stats 
                (timestamp, total_cases, total_deaths, total_recovered, 
                 active_cases, critical_cases, today_cases, today_deaths)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                data['cases'],
                data['deaths'],
                data['recovered'],
                data['active'],
                data.get('critical'),
                data.get('todayCases'),
                data.get('todayDeaths')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"ERROR inserting global stats: {e}")
            return False
    
    def insert_country_stats(self, data: Dict) -> bool:
        """Insert country-specific statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.fromtimestamp(data['updated'] / 1000)
            
            cursor.execute('''
                INSERT INTO country_stats 
                (timestamp, country, total_cases, total_deaths, total_recovered,
                 active_cases, critical_cases, today_cases, today_deaths,
                 population, tests, cases_per_million, deaths_per_million)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                data['country'],
                data['cases'],
                data['deaths'],
                data['recovered'],
                data['active'],
                data.get('critical'),
                data.get('todayCases'),
                data.get('todayDeaths'),
                data.get('population'),
                data.get('tests'),
                data.get('casesPerOneMillion'),
                data.get('deathsPerOneMillion')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"ERROR inserting country stats: {e}")
            return False
    
    def log_error(self, error_type: str, error_message: str, raw_response: str = None):
        """Log errors to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO error_log (error_type, error_message, raw_response)
                VALUES (?, ?, ?)
            ''', (error_type, error_message, raw_response))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"ERROR logging error: {e}")
    
    def get_recent_global_data(self, hours: int = 24) -> List[Dict]:
        """Get recent global data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, total_cases, total_deaths, active_cases, today_cases
            FROM global_stats
            WHERE timestamp > datetime('now', 'localtime', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        ''', (hours,))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                'timestamp': row[0],
                'total_cases': row[1],
                'total_deaths': row[2],
                'active_cases': row[3],
                'today_cases': row[4]
            })
        
        return result
    
    def get_country_trend(self, country: str, days: int = 7) -> List[Dict]:
        """Get trend data for a specific country"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, total_cases, total_deaths, today_cases, today_deaths
            FROM country_stats
            WHERE country = ? 
            AND timestamp > datetime('now', 'localtime', '-' || ? || ' days')
            ORDER BY timestamp DESC
        ''', (country, days))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                'timestamp': row[0],
                'total_cases': row[1],
                'total_deaths': row[2],
                'today_cases': row[3],
                'today_deaths': row[4]
            })
        
        return result

    def get_data_quality_metrics(self, hours: int = 24) -> Dict:
        """Calculate data quality metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Expected data points (one every 10 minutes)
        expected_points = (hours * 60) // 10
        
        # Count actual global data points
        cursor.execute('''
            SELECT COUNT(*) FROM global_stats
            WHERE timestamp > datetime('now', 'localtime', '-' || ? || ' hours')
        ''', (hours,))
        actual_points = cursor.fetchone()[0]
        
        # Count errors
        cursor.execute('''
            SELECT COUNT(*) FROM error_log
            WHERE timestamp > datetime('now', 'localtime', '-' || ? || ' hours')
        ''', (hours,))
        error_count = cursor.fetchone()[0]
        
        # Calculate success rate
        success_rate = (actual_points / expected_points * 100) if expected_points > 0 else 0
        
        conn.close()
        
        return {
            'expected_data_points': expected_points,
            'actual_data_points': actual_points,
            'missing_data_points': expected_points - actual_points,
            'success_rate_percent': round(success_rate, 2),
            'error_count': error_count
        }
    
    def detect_case_surge(self, country: str, threshold_percent: float = 5.0) -> Dict:
        """
        Detect if there's a surge in cases
        Args:
            country: Country name
            threshold_percent: % increase to consider a surge
        Returns: Dict with surge information
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get last two data points
        cursor.execute('''
            SELECT today_cases, timestamp
            FROM country_stats
            WHERE country = ?
            ORDER BY timestamp DESC
            LIMIT 2
        ''', (country,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 2:
            return {'surge_detected': False, 'message': 'Insufficient data'}
        
        current_cases = rows[0][0] or 0
        previous_cases = rows[1][0] or 0
        
        if previous_cases == 0:
            return {'surge_detected': False, 'message': 'No previous data'}
        
        percent_change = ((current_cases - previous_cases) / previous_cases) * 100
        
        return {
            'surge_detected': percent_change > threshold_percent,
            'percent_change': round(percent_change, 2),
            'current_cases': current_cases,
            'previous_cases': previous_cases,
            'threshold': threshold_percent
        }
    
    def get_top_countries_by_today_cases(self, limit: int = 5) -> List[Dict]:
        """Get countries with highest cases today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get most recent timestamp
        cursor.execute('SELECT MAX(timestamp) FROM country_stats')
        latest_time = cursor.fetchone()[0]
        
        if not latest_time:
            return []
        
        # Get top countries at that timestamp
        cursor.execute('''
            SELECT country, today_cases, cases_per_million
            FROM country_stats
            WHERE timestamp = ?
            AND today_cases IS NOT NULL
            ORDER BY today_cases DESC
            LIMIT ?
        ''', (latest_time, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                'country': row[0],
                'today_cases': row[1],
                'cases_per_million': row[2]
            })
        
        return result

# Test it
if __name__ == '__main__':
    db = HealthDatabase('public_health_data.db')
    
    # Test with sample global data
    sample_global = {
        'updated': int(datetime.now().timestamp() * 1000),
        'cases': 700000000,
        'deaths': 7000000,
        'recovered': 675000000,
        'active': 18000000,
        'critical': 50000,
        'todayCases': 50000,
        'todayDeaths': 500
    }
    
    success = db.insert_global_stats(sample_global)
    if success:
        print("✓ Global data inserted successfully")
        
        recent = db.get_recent_global_data(hours=1)
        print(f"✓ Found {len(recent)} recent records")