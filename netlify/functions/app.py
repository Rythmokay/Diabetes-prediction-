from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import os
import sys
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the Flask app from the main app.py
from app import app as flask_app

# Define the handler function for Netlify
def handler(event, context):
    # Parse the request
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    query_string = event.get('queryStringParameters', {})
    body = event.get('body', '')
    
    # Create a Flask test client
    client = flask_app.test_client()
    
    # Make the request to the Flask app
    if http_method == 'GET':
        response = client.get(path, query_string=query_string, headers=headers)
    elif http_method == 'POST':
        response = client.post(path, data=body, headers=headers)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    # Return the response
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.data.decode('utf-8')
    }
