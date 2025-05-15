// Simple build script to prepare Flask templates for Netlify static hosting
const fs = require('fs');
const path = require('path');

// Function to process HTML files and replace Flask/Jinja2 template syntax
function processHtmlFile(filePath) {
  console.log(`Processing ${filePath}...`);
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Replace Flask url_for with static paths
  content = content.replace(/\{\{\s*url_for\('static',\s*filename='([^']*)'\)\s*\}\}/g, '/static/$1');
  
  // Remove or simplify other Flask/Jinja2 syntax that won't work in static HTML
  content = content.replace(/\{%\s*if\s*error\s*%\}([\s\S]*?)\{%\s*endif\s*%\}/g, '');
  
  // Write the processed file
  fs.writeFileSync(filePath, content);
  console.log(`Processed ${filePath}`);
}

// Process all HTML files in templates directory
const templatesDir = path.join(__dirname, 'templates');
const files = fs.readdirSync(templatesDir);

files.forEach(file => {
  if (file.endsWith('.html')) {
    processHtmlFile(path.join(templatesDir, file));
  }
});

// Create a simple _redirects file for Netlify
const redirectsContent = `
/static/* /static/:splat 200
/* /index.html 200
`;

fs.writeFileSync(path.join(templatesDir, '_redirects'), redirectsContent);
console.log('Created _redirects file');

console.log('Build completed successfully!');
