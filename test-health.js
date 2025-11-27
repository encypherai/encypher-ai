const http = require('http');
http.get('http://localhost:8080/api/health', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log('Status:', res.statusCode, 'Body:', data));
}).on('error', e => console.log('Error:', e.message));
