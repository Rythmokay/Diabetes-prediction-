// netlify/functions/app.js
const { spawn } = require('child_process');
const express = require('express');
const serverless = require('serverless-http');
const path = require('path');
const fs = require('fs');

// Create Express app
const app = express();

// Middleware to parse form data
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Serve static files
app.use('/static', express.static(path.join(__dirname, '../../static')));

// Function to execute Python script
const executePython = (script, args = []) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [script, ...args]);
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

// Simple template rendering function
const renderTemplate = (template, data) => {
  let result = template;
  
  // Replace variables
  for (const [key, value] of Object.entries(data)) {
    if (typeof value !== 'object') {
      const regex = new RegExp(`\\{\\{ ${key} \\}\\}`, 'g');
      result = result.replace(regex, value);
    }
  }
  
  // Replace conditionals
  const conditionalRegex = /\{\% if ([^\%]+) \%\}([\s\S]*?)\{\% else \%\}([\s\S]*?)\{\% endif \%\}/g;
  result = result.replace(conditionalRegex, (match, condition, ifTrue, ifFalse) => {
    if (eval(condition.replace('result.', 'data.'))) {
      return ifTrue;
    } else {
      return ifFalse;
    }
  });
  
  // Replace loops
  const loopRegex = /\{\% for ([^\%]+) in ([^\%]+) \%\}([\s\S]*?)\{\% endfor \%\}/g;
  result = result.replace(loopRegex, (match, item, collection, content) => {
    const [itemName, valueName] = item.split(',').map(s => s.trim());
    const collectionName = collection.trim().replace('result.', 'data.');
    let collectionObj;
    
    try {
      collectionObj = eval(collectionName);
    } catch (e) {
      return '';
    }
    
    let output = '';
    if (collectionObj) {
      if (collectionName.includes('.items()')) {
        for (const [key, value] of Object.entries(collectionObj)) {
          let itemContent = content;
          itemContent = itemContent.replace(new RegExp(`\\{\\{ ${itemName} \\}\\}`, 'g'), key);
          itemContent = itemContent.replace(new RegExp(`\\{\\{ ${valueName} \\}\\}`, 'g'), value);
          output += itemContent;
        }
      } else {
        for (const item of collectionObj) {
          output += content.replace(new RegExp(`\\{\\{ ${itemName} \\}\\}`, 'g'), item);
        }
      }
    }
    return output;
  });
  
  return result;
};

// Home route
app.get('/', (req, res) => {
  try {
    const indexHtml = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
    res.send(indexHtml.replace(/\{\{ url_for\('static', filename='([^']+)'\) \}\}/g, '/static/$1'));
  } catch (error) {
    console.error('Error serving index.html:', error);
    res.status(500).send('Error loading the application');
  }
});

// Prediction route
app.post('/predict', async (req, res) => {
  try {
    // Create a temporary JSON file with the form data
    const formData = JSON.stringify(req.body);
    const tempFilePath = path.join(__dirname, 'temp_data.json');
    fs.writeFileSync(tempFilePath, formData);

    // Execute the prediction script
    const scriptPath = path.join(__dirname, 'predict.py');
    const result = await executePython(scriptPath, [tempFilePath]);
    
    // Clean up the temporary file
    try {
      fs.unlinkSync(tempFilePath);
    } catch (e) {
      console.error('Error deleting temp file:', e);
    }

    // Parse the prediction result
    const prediction = JSON.parse(result);
    
    // Read the result template
    const resultTemplate = fs.readFileSync(path.join(__dirname, '../../templates/result.html'), 'utf8');
    
    // Fix static file references
    const templateWithFixedStatic = resultTemplate.replace(
      /\{\{ url_for\('static', filename='([^']+)'\) \}\}/g, 
      '/static/$1'
    );
    
    // Render the template with our data
    const renderedHtml = renderTemplate(templateWithFixedStatic, prediction);
    
    // Send the rendered HTML
    res.send(renderedHtml);
  } catch (error) {
    console.error('Error processing prediction:', error);
    res.status(500).send(`<h1>Error processing your request</h1><p>${error.message}</p><a href="/">Go back</a>`);
  }
});

// Handle all other routes - serve static files or templates if they exist
app.use((req, res) => {
  const requestPath = req.path.substring(1); // Remove leading slash
  
  // Check if this is a template request
  const templatePath = path.join(__dirname, '../../templates', requestPath);
  if (fs.existsSync(templatePath)) {
    const template = fs.readFileSync(templatePath, 'utf8');
    return res.send(template.replace(/\{\{ url_for\('static', filename='([^']+)'\) \}\}/g, '/static/$1'));
  }
  
  // If not found, return 404
  res.status(404).send('<h1>Page not found</h1><a href="/">Go back to home</a>');
});

// Export the serverless handler
module.exports.handler = serverless(app);
