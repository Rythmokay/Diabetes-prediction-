// netlify/functions/api.js
const serverless = require('serverless-http');
const express = require('express');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Create an Express app
const app = express();

// Set up middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, '../../public')));

// Serve the templates directory
app.use('/templates', express.static(path.join(__dirname, '../../templates')));

// Serve the static directory
app.use('/static', express.static(path.join(__dirname, '../../static')));

// Home route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../../templates/index.html'));
});

// Prediction route
app.post('/predict', (req, res) => {
  try {
    // Write the form data to a temporary file
    const formData = JSON.stringify(req.body);
    fs.writeFileSync('/tmp/form_data.json', formData);

    // Execute the Python script with the form data
    const result = execSync(`python ${path.join(__dirname, 'predict.py')}`, {
      env: { ...process.env, FORM_DATA: formData }
    }).toString();

    // Parse the result
    const prediction = JSON.parse(result);

    // Render the result template
    res.send(renderResultTemplate(prediction));
  } catch (error) {
    console.error('Error:', error);
    res.status(500).send('An error occurred during prediction.');
  }
});

// Function to render the result template
function renderResultTemplate(result) {
  const resultHtml = fs.readFileSync(path.join(__dirname, '../../templates/result.html'), 'utf8');
  
  // Replace template variables with actual values
  return resultHtml
    .replace('{{ result.prediction }}', result.prediction)
    .replace('{{ result.probability }}', result.probability)
    .replace('{% for feature, value in result.features.items() %}', '')
    .replace('{% endfor %}', '')
    .replace('<tr>\n                    <td>{{ feature }}</td>\n                    <td>{{ value }}</td>\n                </tr>', 
      Object.entries(result.features).map(([feature, value]) => 
        `<tr>\n                    <td>${feature}</td>\n                    <td>${value}</td>\n                </tr>`
      ).join('\n'));
}

// Export the serverless handler
module.exports.handler = serverless(app);
