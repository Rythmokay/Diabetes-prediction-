const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  // Only allow POST requests
  if (event.httpMethod !== 'POST' && event.httpMethod !== 'OPTIONS') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  // Handle CORS preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: ''
    };
  }

  try {
    // Prepare to run the Python script
    const pythonProcess = spawn('python', [
      path.join(__dirname, 'predict.py'),
      JSON.stringify(event)
    ]);

    // Collect data from script
    let result = '';
    let error = '';

    // Process stdout data
    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    // Process stderr data
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    // Return a promise that resolves when the Python process exits
    return new Promise((resolve, reject) => {
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error(`Python process exited with code ${code}`);
          console.error(`Error: ${error}`);
          resolve({
            statusCode: 500,
            body: JSON.stringify({ error: 'Error processing prediction', details: error })
          });
        } else {
          try {
            const parsedResult = JSON.parse(result);
            resolve({
              statusCode: 200,
              headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
              },
              body: JSON.stringify(parsedResult)
            });
          } catch (e) {
            console.error('Error parsing Python output:', e);
            resolve({
              statusCode: 500,
              body: JSON.stringify({ error: 'Error parsing prediction result', details: result })
            });
          }
        }
      });
    });
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Server error', details: error.message })
    };
  }
};
