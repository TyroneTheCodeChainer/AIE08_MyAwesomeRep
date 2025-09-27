"""
Minimal Session 03 test for Vercel deployment
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "message": "Session 03 Test - Minimal Version",
        "status": "working"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": "minimal"
    })

# Export for Vercel
application = app

if __name__ == '__main__':
    app.run(debug=True)