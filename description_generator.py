import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

load_dotenv()

def generate_description(data):
    word_count = data.get("wordCount", 600)  # handle word count if included

    llm = ChatGroq(
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )

    prompt = ChatPromptTemplate.from_template(f"""
    Generate a professional job post description of around {word_count} words based on the following details:
    - Company Name: {{companyName}}
    - Company Type: {{companyType}}
    - Post For: {{postFor}}
    - Post Type: {{postType}}
    - Location Type: {{location}}
    - Address: {{address}}
    - Job Title: {{title}}
    - Package: {{package}}
    - Last Date: {{lastDate}}
    - Vacancy: {{vacancy}}
    - Skills: {{skills}}
    - Keywords: {{keywords}}

    Here is a draft provided by the user:
    "{{description}}"
     
    
    Instructions:
    - Use the 'companyName' as the actual organization name in the job post.
    - Do **not** mention 'companyType' explicitly in the output.
    - Instead, reflect the nature of the company (based on 'companyType') through tone or wording, using 'companyName' as the face of the organization.
    - Make the job post sound professional, engaging, and polished.
    - Elaborate where needed and ensure it appeals to job seekers.
    - Keep it concise and stick to around {word_count} words.
    -Please improve this draft and make it sound more professional, engaging, and polished.
    Elaborate where needed by yourself and ensure it is clear and compelling to job seekers.
    Stick to around {word_count} words.
    """)

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(data)
    return response