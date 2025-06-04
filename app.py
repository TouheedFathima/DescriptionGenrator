import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from description_generator import generate_description
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)

# Configure CORS to allow requests from Opptiverse
CORS(app, resources={r"/generate": {"origins": "https://app.opptiverse.com"}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    print("Received payload:", data)  # Debug: Log the incoming payload

    # Define mandatory fields with validation rules
    mandatory_fields = {
        "companyType": {"message": "Recruiter Type is required"},
        "postFor": {"message": "Post For is required"},
        "postType": {"message": "Post Type is required"},
        "address": {"message": "Address is required and cannot be empty"},
        "titleCategory": {"message": "Title Category is required and cannot be empty"},
        "title": {"message": "Title is required and cannot be empty"},
        "package": {"message": "Package is required"},
        "lastDate": {"message": "Last Date is required"},
        "vacancy": {"message": "Vacancy must be a positive number", "validate": lambda v: v > 0}
    }

    # Validate mandatory fields
    for field, rule in mandatory_fields.items():
        value = data.get(field)
        print(f"Validating {field}: {value} (type: {type(value)})")  # Debug: Log each field
        if value is None or (rule.get("validate") and not rule["validate"](value)) or (not rule.get("validate") and str(value).strip() == ""):
            return jsonify({"error": rule["message"], "field": field}), 400

    # Process skills and keywords if they are strings (from your frontend)
    if isinstance(data.get("skills"), str):
        data["skills"] = [s.strip() for s in data["skills"].split(",") if s.strip()]
    if isinstance(data.get("keywords"), str):
        data["keywords"] = [k.strip() for k in data["keywords"].split(",") if k.strip()]

    # Validate skills and keywords
    if len(data.get("skills", [])) == 0:
        return jsonify({"error": "At least one skill is required", "field": "skills"}), 400
    if len(data["keywords"]) == 0:
        return jsonify({"error": "At least one keyword is required", "field": "keywords"}), 400

    # Generate the description
    try:
        response = generate_description(data)
        return jsonify({'description': response})
    except Exception as e:
        print("Error in /generate:", str(e))  # Debug: Log any exceptions
        return jsonify({"error": f"Failed to generate description: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)