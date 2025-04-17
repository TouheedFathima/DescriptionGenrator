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

    # Define the prompt template
    prompt = ChatPromptTemplate.from_template("""
    Generate a professional job post description based on the following details:
    - Company Type: {companyType}
    - Post For: {postFor}
    - Position: {position}
    - Location Type: {location}
    - Address: {address}
    - Job Title: {title}
    - Package: {package}
    - Last Date: {lastDate}
    - Vacancy: {vacancy}
    - Skills: {skills}
    - Keywords: {keywords}

    Write it in a natural, engaging way.
    """)

    # Initialize the LLM model (ChatGroq)
    llm = ChatGroq(temperature=0.7, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")

    # Chain the LLM with the prompt
    chain = LLMChain(llm=llm, prompt=prompt)

    # Run the chain with the data
    response = chain.run(data)

    # Return the generated description as a JSON response
    return jsonify({'description': response})

if __name__ == '__main__':
    app.run(debug=True)
