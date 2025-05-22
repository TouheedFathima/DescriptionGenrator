import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from description_generator import generate_description
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    response = generate_description(data)  
    return jsonify({'description': response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)
