from flask import Flask, jsonify
from src.database import HealthDatabase
from config import DB_PATH, COUNTRIES, CASE_INCREASE_THRESHOLD_PERCENT
from datetime import datetime

app = Flask(__name__)
db = HealthDatabase(DB_PATH)
@app.route('/')
def hello():
    return "Flask is working!"

@app.route('/health', methods=['GET'])
def health_check():
    """Check if monitoring system is healthy"""
    try:
        # Check if we have recent data (within last 15 minutes)
        recent_data = db.get_recent_global_data(hours=24)
        
        if not recent_data:
            return jsonify({
                'status': 'unhealthy',
                'message': 'No data in last hour',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # Check data quality
        metrics = db.get_data_quality_metrics(hours=1)
        
        if metrics['success_rate_percent'] < 80:
            return jsonify({
                'status': 'degraded',
                'message': f"Success rate below 80%: {metrics['success_rate_percent']}%",
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }), 200
        
        return jsonify({
            'status': 'healthy',
            'message': 'System operating normally',
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/alerts', methods=['GET'])
def check_alerts():
    """Check for any case surges"""
    alerts = []
    
    for country in COUNTRIES:
        surge_info = db.detect_case_surge(country, CASE_INCREASE_THRESHOLD_PERCENT)
        if surge_info.get('surge_detected'):
            alerts.append({
                'country': country,
                'alert_type': 'case_surge',
                'severity': 'warning',
                'details': surge_info
            })
    
    return jsonify({
        'alert_count': len(alerts),
        'alerts': alerts,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/summary', methods=['GET'])
def get_summary():
    """Get current summary of all monitored countries"""
    top_countries = db.get_top_countries_by_today_cases(limit=10)
    
    return jsonify({
        'top_countries_today': top_countries,
        'monitored_countries': COUNTRIES,
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)