# This script is to "move to linear" button from slack notification ,port=5002#

from flask import Flask, request, jsonify
import requests
import json
import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
    
# Direct configuration values
LINEAR_API_KEY = os.environ.get('LINEAR_API_KEY')
LINEAR_TEAM_ID = os.environ.get('LINEAR_TEAM_ID')
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
SERVICENOW_URL = os.environ.get('SERVICENOW_URL')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

# Validate environment variables
def validate_env_vars():
    required_vars = {
        'LINEAR_API_KEY': LINEAR_API_KEY,
        'LINEAR_TEAM_ID': LINEAR_TEAM_ID,
        'SLACK_BOT_TOKEN': SLACK_BOT_TOKEN,
        'SERVICENOW_URL': SERVICENOW_URL,
        'SLACK_WEBHOOK_URL': SLACK_WEBHOOK_URL
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        app.logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

# Set up logging
def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
   
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
   
    # File Handler
    file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=5)
    file_handler.setFormatter(log_formatter)
   
    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

setup_logging()

# Health check endpoint
@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Slack to Linear Integration Service is running"
    }), 200

# Test connections at startup
def test_linear_connection():
    try:
        headers = {
            "Authorization": f"Bearer {LINEAR_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json={"query": "query { viewer { id } }"}
        )
        if response.status_code == 200:
            app.logger.info("Linear API connection successful")
            return True
        else:
            app.logger.error(f"Linear API test failed: {response.text}")
            return False
    except Exception as e:
        app.logger.error(f"Linear API connection error: {str(e)}")
        return False

def test_slack_connection():
    try:
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.post("https://slack.com/api/auth.test", headers=headers)
        if response.json().get('ok'):
            app.logger.info("Slack API connection successful")
            return True
        else:
            app.logger.error(f"Slack API test failed: {response.text}")
            return False
    except Exception as e:
        app.logger.error(f"Slack API connection error: {str(e)}")
        return False

[Previous format_comments_for_linear function remains the same]

[Previous handle_slack_interaction route remains the same]

[Previous create_linear_ticket function remains the same]

[Previous send_slack_notification function remains the same]

if __name__ == '__main__':
    app.logger.info("Starting Flask application")
    
    if not validate_env_vars():
        app.logger.error("Missing required environment variables. Exiting.")
        sys.exit(1)
    
    # Test connections
    linear_ok = test_linear_connection()
    slack_ok = test_slack_connection()
    
    if not (linear_ok and slack_ok):
        app.logger.warning("One or more API connections failed. Application may not function correctly.")
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5002))
    
    # Start the server
    app.run(host='0.0.0.0', port=port)
