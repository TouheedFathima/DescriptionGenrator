import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import html  # For escaping special characters

load_dotenv()

force_elaboration = True

def clean_html_spacing(html):
    """
    Clean up HTML output by removing extra line breaks and spaces between <li> elements.
    Ensures tight spacing within <ul> lists while preserving spacing between sections.
    """
    cleaned_html = re.sub(r'</li>\s*<li>', '</li><li>', html)
    cleaned_html = re.sub(r'<ul>\s*', '<ul>', cleaned_html)
    cleaned_html = re.sub(r'\s*</ul>', '</ul>', cleaned_html)
    cleaned_html = re.sub(r'</ul>\s*<b>', '</ul><br><br><b>', cleaned_html)
    return cleaned_html

def generate_description(data):
    word_count = data.get("wordCount", 1000) or 1000  # Default to 1000 if missing or falsy
    post_type = (data.get("postType", "") or "")# Default to empty string if missing
    company_name = (data.get("companyName", "") or "Individual").strip()  # Default to "Individual"
    title = html.escape(data.get("title", "") or "Untitled Role")  # Default to "Untitled Role"
    combined_title = title  
    # Default empty lists for skills and keywords
    skills = data.get("skills", []) or []
    keywords = data.get("keywords", []) or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    # Combine important words for bolding (remove duplicates)
    important_words = list(set([company_name] + skills + keywords))
    important_words = [word for word in important_words if word]

    # Clean the description field to remove old error messages
    raw_description = data.get("description", "") or "No additional information provided."
    clean_description = re.sub(r'<[^>]+>', '', raw_description).strip()
    if "Error: Invalid post type" in clean_description:
        additional_info = "No additional information provided."
    else:
        additional_info = raw_description

    # Default format if post_type is missing or invalid
    if not post_type:
        intro_instruction = "Generate a generic job description for a role. The tone should be professional and adaptable to any job type."
        format_instruction = """
Format:
<b>Company:</b> [Company Name]  
<b>Location:</b> [City/Remote/Hybrid (if provided)]  
<b>Role:</b> [Title (if provided)]  

<b>About the Opportunity:</b>  
[Brief intro to the role and company.]

<b>Responsibilities:</b>  
<ul>
    <li>[List of duties (if provided, otherwise generic duties).]</li>
</ul>

<b>Skills & Qualifications:</b>  
<ul>
    <li>[List of skills (if provided, otherwise generic skills).]</li>
</ul>
"""
    elif post_type == "Full time":
        intro_instruction = "Generate a professional full-time job description targeted at attracting qualified candidates. The tone should be formal, aspirational, and highlight long-term career growth, company culture, and stability."
        format_instruction = """
Format:
<b>Company:</b> [Company Name]  
<b>Location:</b> [City/Remote/Hybrid]  
<b>Job Type:</b> Full-Time  

<b>About the Company:</b>  
[Brief intro to the company, culture, and mission.]

<b>Roles & Responsibilities:</b>  
<ul>
    <li>[List of job duties.]</li>
</ul>

<b>Required Skills & Qualifications:</b>  
<ul>
    <li>[List of skills and qualifications.]</li>
</ul>

<b>Benefits:</b>  
<ul>
    <li>[Perks like health insurance, paid leave, etc.]</li>
</ul>
"""
    elif post_type == "Part time":
        intro_instruction = "Generate a clear and professional part-time job description. Highlight flexible hours, key responsibilities, and the specific time commitment required. Keep the tone friendly yet informative."
        format_instruction = """
Format:
<b>Company:</b> [Company Name]  
<b>Location:</b> [City/Remote/Hybrid]  
<b>Job Type:</b> Part-Time  

<b>About the Role:</b>  
[Brief about the role and work hours.]

<b>Key Responsibilities:</b>  
<ul>
    <li>[List of duties.]</li>
</ul>

<b>Qualifications & Skills:</b>  
<ul>
    <li>[List key skills.]</li>
</ul>

<b>Perks:</b>  
<ul>
    <li>[Highlight work-life balance, flexibility.]</li>
</ul>
"""
    elif post_type == "Internship (Stipend)":
        intro_instruction = "Create a paid internship post that is inviting to students or fresh graduates. Emphasize learning, mentorship, potential growth opportunities, and the stipend as a financial incentive. Keep the tone encouraging and professional."
        format_instruction = """
Format: 
<b>Company:</b> [Company Name]  
<b>Location:</b> [City/Remote/Hybrid]  
<b>Internship Type:</b> Paid Internship  

<b>About the Company:</b>  
[Brief overview.]

<b>Internship Overview:</b>  
[What interns will work on.]

<b>Learning Opportunities:</b>  
<ul>
    <li>[List skills interns will develop.]</li>
</ul>

<b>Requirements:</b>  
<ul>
    <li>[Eligibility, background, or tools.]</li>
</ul>

<b>Key Responsibilities:</b>  
<ul>
    <li>[List of duties.]</li>
</ul>

<b>Stipend:</b> [Monthly stipend amount (if provided)]  
<b>Duration:</b> [X weeks/months (if provided)]  
"""
    elif post_type == "Internship (Unpaid)":
        intro_instruction = "Create an unpaid internship post that is inviting to students or fresh graduates. Emphasize learning, mentorship, networking opportunities, and other non-monetary benefits to attract candidates. Keep the tone encouraging and professional."
        format_instruction = """
Format: 
<b>Company:</b> [Company Name]  
<b>Location:</b> [City/Remote/Hybrid]  
<b>Internship Type:</b> Unpaid Internship  

<b>About the Company:</b>  
[Brief overview.]

<b>Internship Overview:</b>  
[What interns will work on.]

<b>Learning Opportunities:</b>  
<ul>
    <li>[List skills interns will develop.]</li>
</ul>

<b>Requirements:</b>  
<ul>
    <li>[Eligibility, background, or tools.]</li>
</ul>

<b>Key Responsibilities:</b>  
<ul>
    <li>[List of duties.]</li>
</ul>

<b>Non-Monetary Benefits:</b>  
<ul>
    <li>[Highlight mentorship, networking, certificates, etc.]</li>
</ul>

<b>Duration:</b> [X weeks/months (if provided)]  
"""
    elif post_type == "Contract":
        intro_instruction = "Generate a professional contract opportunity post. Focus on short-term project deliverables, duration, and payment. It is not a job. The tone should appeal to freelancers or short-term collaborators."
        format_instruction = f"""
Format:
<b>Contract Role:</b> {combined_title}  
<b>Location:</b> [On-site/Remote (if provided)]  
<b>Type:</b> Contract-Based (X months if provided)  

<b>Overview:</b>  
[Short intro to project.]

<b>Responsibilities:</b>  
<ul>
    <li>[List of deliverables.]</li>
</ul>

<b>Requirements:</b>  
<ul>
    <li>[Tools, skills, experience needed.]</li>
</ul>

<b>Contract Duration:</b> [e.g., 6 months (if provided)]  
"""
    elif post_type == "Project (freelancers)":
        intro_instruction = "Generate a project collaboration post for individual freelancers. This is not a job but an opportunity for freelancers to contribute to a specific project with clear goals and timelines. Focus on skillset needed, project objectives, and payment terms. Keep the tone flexible and appealing to independent professionals."
        format_instruction = """
Format:
<b>Company Name:</b> [Company]  
<b>Location:</b> [Remote/On-site/Hybrid (if provided)]  

<b>Project Overview:</b>  
[Summary of the project, its impact, and goals.]

<b>Who We're Looking For:</b>  
[Type of freelancers, e.g., independent professionals with specific skills.]

<b>Required Skills:</b>  
<ul>
    <li>[List of technical/non-technical skills.]</li>
</ul>

<b>Timeline:</b> [Expected duration or milestones (if provided)]  
"""
    elif post_type == "Project (Service companies)":
        intro_instruction = "Generate a project collaboration post for service companies. This is not a job but an opportunity for companies to collaborate on a specific project with clear goals and timelines. Focus on partnership potential, project scale, and required expertise. Keep the tone formal and professional."
        format_instruction = """
Format:
<b>Company Name:</b> [Company]  
<b>Location:</b> [Remote/On-site/Hybrid (if provided)]  

<b>Project Overview:</b>  
[Summary of the project, its impact, and goals.]

<b>Who We're Looking For:</b>  
[Type of service companies, e.g., agencies or firms with specific expertise.]

<b>Required Expertise:</b>  
<ul>
    <li>[List of technical/non-technical expertise required.]</li>
</ul>

<b>Collaboration Scope:</b>  
[Details on how the collaboration will work.]

<b>Timeline:</b> [Expected duration or milestones (if provided)]  
"""
    else:
        # Use a generic format instead of returning an error
        intro_instruction = "Generate a generic job description for a role. The tone should be professional and adaptable to any job type."
        format_instruction = """
Format:
<b>Company:</b> [Company Name]  
<b>Location:</b> [City/Remote/Hybrid (if provided)]  
<b>Role:</b> [Title (if provided)]  

<b>About the Opportunity:</b>  
[Brief intro to the role and company.]

<b>Responsibilities:</b>  
<ul>
    <li>[List of duties (if provided, otherwise generic duties).]</li>
</ul>

<b>Skills & Qualifications:</b>  
<ul>
    <li>[List of skills (if provided, otherwise generic skills).]</li>
</ul>
"""

    # LLM setup
    llm = ChatGroq(
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )

    # Full prompt with dynamic instructions
    location = data.get("location", "") or "Not specified"
    package = data.get("package", "") or "Competitive compensation"
    last_date = data.get("lastDate", "") or "Not specified"
    vacancy = data.get("vacancy", 1) if data.get("vacancy") and data.get("vacancy") > 0 else 1

    prompt = ChatPromptTemplate.from_template(f"""
    {intro_instruction}

    Generate a professional and polished opportunity post using the following details:

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

    Important words to bold: {', '.join(important_words) if important_words else 'None'}

    {format_instruction}

    Instructions:
    - Use only <b>, not ** for bold.
    - Your response should be suitable for direct copy-pasting into a web page or email client that supports HTML formatting. Use only valid HTML tags.
    - Use bullet points where appropriate.
    - For all <ul> lists, ensure there are NO extra line breaks or spaces between <li> elements.
    - Ensure exactly two <br> tags between sections for clean spacing.
    - Output should be ready to copy-paste into LinkedIn/email without editing.
    - Use the company name naturally — don’t include 'companyType'.
    - Strictly follow the format provided above. Do NOT add extra fields or sections.
    - Within paragraph sections, bold the important words listed above using <b> tags. Do NOT bold words within <ul> lists.
    - Ensure the response is at least {word_count} words. Expand each section thoughtfully with relevant details.
    - Make the tone fit the nature of the role (e.g., formal for full-time, friendly for internships).
    - If any field is missing or empty, use generic placeholders (e.g., 'Not specified' for location, 'Competitive compensation' for package).

Additional Info Provided by User:
{additional_info}
    """)

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({
        "companyName": company_name,
        "postFor": data.get("postFor", "Not specified"),
        "postType": post_type or "Generic Role",
        "location": location,
        "address": data.get("address", "Not specified"),
        "title": title,
        "package": package,
        "lastDate": last_date,
        "vacancy": vacancy,
        "skills": ", ".join(skills) if skills else "Not specified",
        "keywords": ", ".join(keywords) if keywords else "Not specified"
    })
    cleaned_response = clean_html_spacing(response)
    return cleaned_response