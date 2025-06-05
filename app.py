import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from description_generator import generate_description
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

CORS(app)  # Allow all origins for debugging

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    print("Received payload:", data)  # Debug: Log the incoming payload

    # Process skills and keywords if they are strings (from your frontend)
    if isinstance(data.get("skills"), str):
        data["skills"] = [s.strip() for s in data["skills"].split(",") if s.strip()]
    if isinstance(data.get("keywords"), str):
        data["keywords"] = [k.strip() for k in data["keywords"].split(",") if k.strip()]

    # Log processed skills and keywords
    skills = data.get("skills", [])
    keywords = data.get("keywords", [])
    print(f"Processed skills: {skills}, keywords: {keywords}")  # Debug: Log processed values

    # Generate the description without validation
    try:
        response = generate_description(data)
        print("Generated description:", response[:100] + "...")  # Debug: Log the first 100 chars of the response
        return jsonify({'description': response})
    except Exception as e:
        print("Error in /generate:", str(e))  # Debug: Log any exceptions
        return jsonify({"error": f"Failed to generate description: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port, debug=True)  # Debug mode for better error logging