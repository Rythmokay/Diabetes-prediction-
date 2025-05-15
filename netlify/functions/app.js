// Netlify serverless function to run the Flask application
const { spawn } = require('child_process');
const path = require('path');

exports.handler = async function(event, context) {
  // Set up the path to the Flask application
  const appPath = path.join(process.cwd(), 'app.py');
  
  try {
    // Execute the Flask application
    const python = spawn('python', [appPath]);
    
    // Wait for the Flask application to start
    await new Promise((resolve, reject) => {
      python.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        if (data.includes('Running on')) {
          resolve();
        }
      });
      
      python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        if (data.includes('Running on')) {
          resolve();
        }
      });
      
      python.on('error', (error) => {
        console.error(`error: ${error.message}`);
        reject(error);
      });
      
      python.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        if (code !== 0) {
          reject(new Error(`Process exited with code ${code}`));
        }
      });
    });
    
    // Forward the request to the Flask application
    const url = new URL(event.path, 'http://localhost:5000');
    const response = await fetch(url, {
      method: event.httpMethod,
      headers: event.headers,
      body: event.body
    });
    
    // Return the response from the Flask application
    return {
      statusCode: response.status,
      headers: Object.fromEntries(response.headers.entries()),
      body: await response.text()
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to execute Flask application' })
    };
  }
};
