// netlify/functions/predict.js
const { spawn } = require('child_process');
const path = require('path');

// Function to execute Python script
const executePython = (scriptPath, args = []) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [scriptPath, ...args]);
    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${stderr}`));
      } else {
        resolve(stdout);
      }
    });
  });
};

exports.handler = async (event, context) => {
  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method Not Allowed' })
    };
  }

  try {
    // Parse the request body
    const body = JSON.parse(event.body);
    
    // Create a JSON string of the form data
    const formDataJson = JSON.stringify(body);
    
    // Execute the Python prediction script
    const scriptPath = path.join(__dirname, 'predict_handler.py');
    const result = await executePython(scriptPath, [formDataJson]);
    
    // Return the prediction result
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: result
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
