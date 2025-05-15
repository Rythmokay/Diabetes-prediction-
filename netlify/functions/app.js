const { execSync } = require('child_process');
const path = require('path');

// Import the Python handler
let pythonHandler;
try {
  // Use Python's importlib to dynamically load the handler
  pythonHandler = require('./flask_adapter.js');
} catch (error) {
  console.error('Failed to import Python handler:', error);
}

exports.handler = async (event, context) => {
  // Set up CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
  };

  // Handle OPTIONS requests (CORS preflight)
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    // Install required Python packages if needed
    try {
      execSync('pip show flask numpy pandas scikit-learn', { stdio: 'ignore' });
    } catch (e) {
      console.log('Installing required packages...');
      execSync('pip install flask numpy pandas scikit-learn joblib', { stdio: 'inherit' });
    }

    // Use the Python handler directly if available
    if (pythonHandler && pythonHandler.handler) {
      return await pythonHandler.handler(event, context);
    }

    // If direct import failed, use the Python script via execSync
    const pythonScript = path.join(__dirname, 'flask_adapter.py');
    const eventData = JSON.stringify(event);
    
    // Write event data to a temporary file to avoid command line length limitations
    const fs = require('fs');
    const tempFile = path.join('/tmp', `event-${Date.now()}.json`);
    fs.writeFileSync(tempFile, eventData);
    
    // Execute the Python script
    const command = `python -c "import sys, json; sys.path.append('${__dirname}'); from flask_adapter import handler; event = json.load(open('${tempFile}')); print(json.dumps(handler(event, {})));"`;
    const result = execSync(command, { encoding: 'utf8' });
    
    // Clean up temporary file
    fs.unlinkSync(tempFile);
    
    // Parse and return the result
    const pythonResult = JSON.parse(result);
    return pythonResult;
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Server error', 
        message: error.message,
        stack: error.stack 
      })
    };
  }
};
