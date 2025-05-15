import sys
import json
import os
import base64
from io import StringIO
import traceback
from urllib.parse import parse_qs

# Add the project root to the path so we can import from app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def handler(event, context):
    try:
        # Import the Flask app
        from app import app, train_model
        
        # Ensure the model is trained
        train_model()
        
        # Parse the event data
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters', {}) or {}
        body = event.get('body', '')
        
        # Create a Flask-like environment
        environ = {
            'PATH_INFO': path,
            'REQUEST_METHOD': http_method,
            'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in query_params.items()]) if query_params else '',
            'SERVER_NAME': 'netlify',
            'SERVER_PORT': '443',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.url_scheme': 'https',
            'wsgi.input': StringIO(body if body else ''),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'HTTP_HOST': headers.get('host', 'netlify.app'),
            'CONTENT_LENGTH': str(len(body)) if body else '0',
            'CONTENT_TYPE': headers.get('content-type', 'application/json'),
        }
        
        # Add headers
        for header, value in headers.items():
            key = 'HTTP_' + header.upper().replace('-', '_')
            environ[key] = value
        
        # Handle form data for POST requests
        if http_method == 'POST' and body:
            if headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
                # Handle form data
                form_data = parse_qs(body)
                environ['wsgi.input'] = StringIO(body)
            elif headers.get('content-type', '').startswith('application/json'):
                try:
                    # Handle JSON data
                    json_body = json.loads(body)
                    environ['wsgi.input'] = StringIO(json.dumps(json_body))
                except:
                    pass
        
        # Create a function to capture the response
        response_status = [200]
        response_headers = []
        
        def start_response(status, headers):
            status_code = int(status.split()[0])
            response_status[0] = status_code
            response_headers.extend(headers)
        
        # Call the Flask app
        response_body = b''
        for data in app(environ, start_response):
            if isinstance(data, str):
                response_body += data.encode('utf-8')
            else:
                response_body += data
        
        # Convert headers to a dictionary
        headers_dict = {}
        for header, value in response_headers:
            headers_dict[header] = value
        
        # Add CORS headers
        headers_dict['Access-Control-Allow-Origin'] = '*'
        headers_dict['Access-Control-Allow-Headers'] = 'Content-Type'
        headers_dict['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        
        # Return the response
        return {
            'statusCode': response_status[0],
            'headers': headers_dict,
            'body': base64.b64encode(response_body).decode('utf-8'),
            'isBase64Encoded': True
        }
        
    except Exception as e:
        # Handle errors
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }
