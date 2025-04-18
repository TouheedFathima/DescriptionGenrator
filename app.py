import os
from flask import Flask, request, jsonify, render_template
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json

    # Extract wordCount separately
    word_count = data.get('wordCount', 500)

    # Join eligibility and benefits into strings for the prompt
    eligibility = ', '.join(data.get('eligibility', []))
    benefits = ', '.join(data.get('benefits', []))

    # Define the prompt template
    prompt = ChatPromptTemplate.from_template(f"""
    Generate a professional job post description of around {word_count} words based on the following details:

    - Company Type: {{companyType}}
    - Post For: {{postFor}}
    - Position: {{position}}
    - Location Type: {{location}}
    - Address: {{address}}
    - Job Title: {{title}}
    - Package: {{package}}
    - Last Date: {{lastDate}}
    - Vacancy: {{vacancy}}
    - Skills: {{skills}}
    - Keywords: {{keywords}}
    - Eligibility: {{eligibility}}
    - Benefits: {{benefits}}

    Write it in a natural, engaging way.
    The description should be around {word_count} words. Don’t go much over or under.
    """)

    # Initialize the LLM model
    llm = ChatGroq(
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )

    # Chain the LLM with the prompt
    chain = LLMChain(llm=llm, prompt=prompt)

    # Run the chain with the provided data
    response = chain.run(data)

    # Return the generated description
    return jsonify({'description': response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)
