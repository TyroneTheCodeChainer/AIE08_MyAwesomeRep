// Minimal Node.js API for Vercel - This should definitely work
export default function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Super simple response - this should work
  res.status(200).json({
    message: 'SUCCESS! Session 03 RAG System is working!',
    status: 'ok',
    timestamp: new Date().toISOString(),
    path: req.url,
    method: req.method
  });
}