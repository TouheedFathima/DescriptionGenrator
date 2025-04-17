import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

load_dotenv()

def generate_description(data):
    llm = ChatGroq(temperature=0.7, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")

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

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(data)
    return response
