import os
import re  # Added for email validation
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from description_generator import generate_description, generate_pass_opportunity_description
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

    # Define mandatory fields with validation rules
    mandatory_fields = {
        "companyType": {"field_name": "Recruiter Type"},
        "postFor": {"field_name": "Post For"},
        "postType": {"field_name": "Post Type"},
        "address": {"field_name": "Address"},
        "title": {"field_name": "Title"},
        "package": {"field_name": "Package"},
        "lastDate": {"field_name": "Last Date"},
        "vacancy": {"field_name": "Vacancy", "validate": lambda v: v > 0}
    }

    # Validate mandatory fields (allow missing fields to be handled by description_generator.py)
    for field, rule in mandatory_fields.items():
        value = data.get(field)
        field_name = rule["field_name"]
        print(f"Validating {field}: {value} (type: {type(value)})")  # Debug: Log each field
        # Skip validation for missing fields; description_generator.py will use defaults
        if value is None:
            print(f"Field '{field_name}' is missing, will use default in description_generator.py")
            continue
        # Validate if the field is present but empty
        if not rule.get("validate") and str(value).strip() == "":
            return jsonify({"error": f"Required field '{field_name}' is empty, please fill it.", "field": field, "value": value}), 400
        # Validate if the field has a specific rule (e.g., vacancy > 0)
        if rule.get("validate") and not rule["validate"](value):
            return jsonify({"error": f"Required field '{field_name}' must be a positive number, please correct it.", "field": field, "value": value}), 400

    # Process skills and keywords if they are strings (from your frontend)
    if isinstance(data.get("skills"), str):
        data["skills"] = [s.strip() for s in data["skills"].split(",") if s.strip()]
    if isinstance(data.get("keywords"), str):
        data["keywords"] = [k.strip() for k in data["keywords"].split(",") if k.strip()]

    # Validate skills and keywords (allow defaults if missing)
    skills = data.get("skills", [])
    keywords = data.get("keywords", [])
    print(f"Processed skills: {skills}, keywords: {keywords}")  
    if len(skills) == 0:
        print("Skills are missing or empty, will use default in description_generator.py")
        data["skills"] = [] 
    if len(keywords) == 0:
        print("Keywords are missing or empty, will use default in description_generator.py")
        data["keywords"] = []  

    # Generate the description
    try:
        response = generate_description(data)
        print("Generated description:", response[:100] + "...") 
        return jsonify({'description': response})
    except Exception as e:
        print("Error in /generate:", str(e))  # Debug: Log any exceptions
        return jsonify({"error": f"Failed to generate description: {str(e)}"}), 500

@app.route('/pass-opportunity', methods=['POST'])
def pass_opportunity():
    # Placeholder endpoint to handle the passOpportunity() function in script.js

    data = request.json
    print("Received payload for /pass-opportunity:", data)  
    return jsonify({"message": "Opportunity passed successfully!"})

@app.route('/pass-opportunity-generate', methods=['POST'])
def pass_opportunity_generate():
    data = request.json
    print("Received payload for /pass-opportunity-generate:", data)  # Debug: Log the incoming payload

    # Define mandatory fields with validation rules
    mandatory_fields = {
        "companyName": {"field_name": "Company Name"},
        "opportunityTitle": {"field_name": "Opportunity Title"},
        "opportunityType": {"field_name": "Opportunity Type"},
        "location": {"field_name": "Location"},
        "workMode": {"field_name": "Work Mode"},
        "numberOfOpenings": {"field_name": "Number of Openings", "validate": lambda v: v > 0},
        "lastDate": {"field_name": "Last Date to Apply"},
        "skillsRequired": {"field_name": "Skills Required", "validate": lambda v: len([s.strip() for s in v.split(",") if s.strip()]) > 0},
        "timeCommitment": {"field_name": "Time Commitment"},
        "recruiterName": {"field_name": "Recruiter Name"},
        "phoneNumber": {"field_name": "Phone Number", "validate": lambda v: len(v.replace("[^0-9]", "")) >= 10},
        "emailAddress": {"field_name": "Email Address", "validate": lambda v: bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v))},
        "salaryMin": {"field_name": "Minimum Salary", "validate": lambda v: v >= 0},
        "salaryMax": {"field_name": "Maximum Salary", "validate": lambda v: v >= 0}
    }

    # Validate mandatory fields
    for field, rule in mandatory_fields.items():
        value = data.get(field)
        field_name = rule["field_name"]
        print(f"Validating {field}: {value} (type: {type(value)})")  # Debug: Log each field
        # Skip validation for missing fields; description_generator.py will use defaults
        if value is None:
            print(f"Field '{field_name}' is missing, will use default in description_generator.py")
            continue
        # Validate if the field is present but empty
        if not rule.get("validate") and str(value).strip() == "":
            return jsonify({"error": f"Required field '{field_name}' is empty, please fill it.", "field": field, "value": value}), 400
        # Validate if the field has a specific rule
        if rule.get("validate") and not rule["validate"](value):
            error_msg = f"Required field '{field_name}' is invalid, please correct it."
            if field == "numberOfOpenings":
                error_msg = f"Required field '{field_name}' must be a positive number, please correct it."
            elif field == "phoneNumber":
                error_msg = f"Required field '{field_name}' must be a valid phone number (at least 10 digits), please correct it."
            elif field == "emailAddress":
                error_msg = f"Required field '{field_name}' must be a valid email address, please correct it."
            elif field in ["salaryMin", "salaryMax"]:
                error_msg = f"Required field '{field_name}' must be a non-negative number, please correct it."
            return jsonify({"error": error_msg, "field": field, "value": value}), 400

    # Validate salary range
    salary_min = data.get("salaryMin", 0)
    salary_max = data.get("salaryMax", 0)
    if salary_min > salary_max:
        return jsonify({"error": "Maximum salary must be greater than or equal to minimum salary", "field": "salaryMax", "value": salary_max}), 400

    # Process skillsRequired if it’s a string
    if isinstance(data.get("skillsRequired"), str):
        data["skillsRequired"] = [s.strip() for s in data["skillsRequired"].split(",") if s.strip()]

    # Ensure salaryOptions is a list (already handled in script.js, but confirm here)
    salary_options = data.get("salaryOptions", [])
    data["salaryOptions"] = salary_options if isinstance(salary_options, list) else []

    # Generate the description
    try:
        response = generate_pass_opportunity_description(data)
        print("Generated description for /pass-opportunity-generate:", response[:100] + "...")  # Debug: Log the first 100 chars of the response
        return jsonify({'description': response})
    except Exception as e:
        print("Error in /pass-opportunity-generate:", str(e))  # Debug: Log any exceptions
        return jsonify({"error": f"Failed to generate description: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port, debug=True)  # Debug mode for better error logging