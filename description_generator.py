import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

load_dotenv()

def generate_description(data):
    word_count = data.get("wordCount", 600)
    post_type = data.get("postType", "").lower()

    # Instructions for different post types
    if post_type == "full time":
        intro_instruction = "Generate a professional full-time job description targeted at attracting qualified candidates. The tone should be formal, aspirational, and highlight long-term career growth, company culture, and stability."
        format_instruction = """
Format:
**Job Title:** [Title]  
**Company:** [Company Name]  
**Location:** [City/Remote/Hybrid]  
**Job Type:** Full-Time  

**About the Company:**  
[Brief intro to the company, culture, and mission.]

**Roles & Responsibilities:**  
[List of job duties.]

**Required Skills & Qualifications:**  
[List of skills and qualifications.]

**Benefits:**  
[Perks like health insurance, paid leave, etc.]

**How to Apply:**  
[Application link or contact email.]

**Application Deadline:** [Date]
"""

    elif post_type == "part time":
        intro_instruction = "Generate a clear and professional part-time job description. Highlight flexible hours, key responsibilities, and the specific time commitment required. Keep the tone friendly yet informative."
        format_instruction = """
Format:
**Job Title:** [Title]  
**Company:** [Company Name]  
**Location:** [City/Remote/Hybrid]  
**Job Type:** Part-Time  

**About the Role:**  
[Brief about the role and work hours.]

**Key Responsibilities:**  
[List of duties.]

**Qualifications & Skills:**  
[List key skills.]

**Perks:**  
[Highlight work-life balance, flexibility.]

**How to Apply:**  
[Application link or contact email.]

**Last Date to Apply:** [Date]
"""

    elif post_type == "internship":
        intro_instruction = "Create an internship post that is inviting to students or fresh graduates. Emphasize learning, mentorship, and potential growth opportunities. Keep the tone encouraging and professional."
        format_instruction = """
Format:
**Internship Position:** [Title]  
**Company:** [Company Name]  
**Location:** [City/Remote/Hybrid]  
**Internship Type:** Full-Time/Part-Time Internship  

**About the Company:**  
[Brief overview.]

**Internship Overview:**  
[What interns will work on.]

**Learning Opportunities:**  
[List skills interns will develop.]

**Requirements:**  
[Eligibility, background, or tools.]

**Stipend:** [If applicable]  
**Duration:** [X weeks/months]  

**How to Apply:**  
[Link or contact info.]

**Deadline to Apply:** [Date]
"""

    elif post_type == "contract":
        intro_instruction = "Generate a professional contract opportunity post. Focus on short-term project deliverables, duration, and payment. It is not a job. The tone should appeal to freelancers or short-term collaborators."
        format_instruction = """
Format:
**Contract Role:** [Title]  
**Company:** [Company Name]  
**Location:** [On-site/Remote]  
**Type:** Contract-Based (X months)  

**Overview:**  
[Short intro to project and company.]

**Responsibilities:**  
[List of deliverables.]

**Requirements:**  
[Tools, skills, experience needed.]

**Contract Duration:** [e.g., 6 months]  
**Compensation:** [Monthly/Total contract value]  

**How to Apply:**  
[Instructions for applying.]

**Deadline to Apply:** [Date]
"""

    elif post_type == "project":
        intro_instruction = "Generate a project collaboration post. This is not a job but an opportunity to contribute to a specific project with clear goals and timelines. Focus on skillset needed and project objectives."
        format_instruction = """
Format:
**Project Title:** [Title]  
**Initiated By:** [Company or Individual Name]  
**Location:** [Remote/On-site/Hybrid]  

**Project Overview:**  
[Summary of the project, its impact, and goals.]

**Who We're Looking For:**  
[Type of collaborators or freelancers.]

**Required Skills:**  
[List of technical/non-technical skills.]

**Timeline:** [Expected duration or milestones]  
**Compensation:** [If applicable]  
**Collaboration Type:** [Individual/Team-based/Volunteer/Grant-funded]  

**How to Join:**  
[Application instructions or contact.]

**Deadline to Show Interest:** [Date]
"""
    else:
        intro_instruction = "Generate a professional opportunity description based on the information provided. Adjust the tone based on the nature of the post."
        format_instruction = ""

    # LLM setup
    llm = ChatGroq(
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )

    # Full prompt with dynamic instructions
    additional_info = data.get("description", "")
    prompt = ChatPromptTemplate.from_template(f"""
    {intro_instruction}

    Generate a professional and polished {post_type} opportunity post using the following details:

    - Company Name: {{companyName}}
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

    {format_instruction}

    Instructions:
    - Use the company name naturally — don’t include 'companyType'.
    - Follow the format above as a structure guide.
    - Make the tone and wording fit the nature of the role (e.g., formal for full-time, friendly for internships).
    - Keep the content concise and within around {word_count} words.

Additional Info Provided by User:
{additional_info}
    """)



    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(data)
    return response


