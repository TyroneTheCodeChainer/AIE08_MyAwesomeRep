"""
Session 03: Debug version to test OpenAI API key
===============================================
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html>
<head><title>Debug Session 03</title></head>
<body>
    <h1>Session 03 Debug</h1>
    <button onclick="checkAPI()">Check API Key Status</button>
    <div id="result"></div>

    <script>
        function checkAPI() {
            fetch('/debug-api')
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML =
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            });
        }
    </script>
</body>
</html>"""

@app.route('/debug-api')
def debug_api():
    """Debug endpoint to check OpenAI API key status."""
    api_key = os.getenv('OPENAI_API_KEY')

    return jsonify({
        'api_key_exists': bool(api_key),
        'api_key_length': len(api_key) if api_key else 0,
        'api_key_prefix': api_key[:7] + '...' if api_key else 'None',
        'all_env_vars': list(os.environ.keys())
    })

if __name__ == '__main__':
    app.run(debug=True)