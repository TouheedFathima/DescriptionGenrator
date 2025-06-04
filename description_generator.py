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
    # Replace multiple line breaks and spaces between </li> and <li> with a single occurrence
    cleaned_html = re.sub(r'</li>\s*<li>', '</li><li>', html)
    # Remove any leading/trailing spaces within <ul> tags
    cleaned_html = re.sub(r'<ul>\s*', '<ul>', cleaned_html)
    cleaned_html = re.sub(r'\s*</ul>', '</ul>', cleaned_html)
    # Ensure consistent section spacing (e.g., two <br> tags between sections)
    cleaned_html = re.sub(r'</ul>\s*<b>', '</ul><br><br><b>', cleaned_html)
    return cleaned_html

def generate_description(data):
    word_count = data.get("wordCount", 1000)
    post_type = data.get("postType", "").lower()

    # Extract skills and keywords for bolding
    skills = data.get("skills", [])
    keywords = data.get("keywords", [])
    company_name = data.get("companyName", "").strip()
    # Escape the titleCategory and title for HTML to handle special characters like "&"
    title_category = html.escape(data.get("titleCategory", ""))
    title = html.escape(data.get("title", ""))
    # Combine for use in contract post type or paragraphs
    combined_title = f"{title_category} - {title}" if title_category and title else title or title_category

    # Convert skills and keywords to lists if they are strings
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    # Combine important words for bolding (remove duplicates)
    important_words = list(set([company_name] + skills + keywords))
    # Filter out empty strings
    important_words = [word for word in important_words if word]

    # Instructions for different post types
    if post_type == "full time":
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

    elif post_type == "part time":
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

    elif post_type == "internship(stipend)":
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

<b>Stipend:</b> [Monthly stipend amount]  
<b>Duration:</b> [X weeks/months]  
"""

    elif post_type == "internship(unpaid)":
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

<b>Duration:</b> [X weeks/months]  
"""

    elif post_type == "contract":
        intro_instruction = "Generate a professional contract opportunity post. Focus on short-term project deliverables, duration, and payment. It is not a job. The tone should appeal to freelancers or short-term collaborators."
        format_instruction = f"""
Format:
<b>Contract Role:</b> {combined_title}  
<b>Location:</b> [On-site/Remote]  
<b>Type:</b> Contract-Based (X months)  

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

<b>Contract Duration:</b> [e.g., 6 months]  
<b>Compensation:</b> [Monthly/Total contract value]  
<b>Deadline to Apply:</b> [Date]
"""

    elif post_type == "project(freelancers)":
        intro_instruction = "Generate a project collaboration post for individual freelancers. This is not a job but an opportunity for freelancers to contribute to a specific project with clear goals and timelines. Focus on skillset needed, project objectives, and payment terms. Keep the tone flexible and appealing to independent professionals."
        format_instruction = """
Format:
<b>Company Name:</b> [Company]  
<b>Location:</b> [Remote/On-site/Hybrid]  

<b>Project Overview:</b>  
[Summary of the project, its impact, and goals.]

<b>Who We're Looking For:</b>  
[Type of freelancers, e.g., independent professionals with specific skills.]

<b>Required Skills:</b>  
<ul>
    <li>[List of technical/non-technical skills.]</li>
</ul>

<b>Timeline:</b> [Expected duration or milestones]  
<b>Compensation:</b> [Payment terms for freelancers]  
"""

    elif post_type == "project(service companies)":
        intro_instruction = "Generate a project collaboration post for service companies. This is not a job but an opportunity for companies to collaborate on a specific project with clear goals and timelines. Focus on partnership potential, project scale, and required expertise. Keep the tone formal and professional."
        format_instruction = """
Format:
<b>Company Name:</b> [Company]  
<b>Location:</b> [Remote/On-site/Hybrid]  

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

<b>Timeline:</b> [Expected duration or milestones]  
"""
    else:
        # Fallback for unmatched post_type
        return f"<b>Error:</b> Invalid post type '{post_type}'. Please select a valid post type (e.g., Full time, Part time, Internship(Stipend), Internship(Unpaid), Contract, Project(Freelancers), Project(Service Companies))."

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
    - Job Title Category: {{titleCategory}}
    - Job Title: {{title}}
    - Package: {{package}}
    - Last Date: {{lastDate}}
    - Vacancy: {{vacancy}}
    - Skills: {{skills}}
    - Keywords: {{keywords}}

    Important words to bold: {', '.join(important_words)}

    {format_instruction}

    Instructions:
    - Use only <b>, not ** for bold. If you output any Markdown, I will fail you 😅 
    - Your response should be suitable for direct copy-pasting into a web page or an email client that supports HTML formatting. Avoid all markdown and use only valid HTML tags for formatting.
    - Use bullet points where appropriate.
    - For all <ul> lists, ensure there are NO extra line breaks or spaces between <li> elements. The <li> tags must be directly consecutive, like this: <ul><li>Item 1</li><li>Item 2</li></ul>. Do NOT add any spaces or line breaks between </li> and <li>.
    - Ensure exactly two <br> tags between sections (e.g., between </ul> and the next <b> heading) for clean spacing.
    - Output should be ready to copy-paste into LinkedIn/email without editing.
    - Use the company name naturally — don’t include 'companyType'.
    - **Strictly follow the format provided above. Do NOT add any extra fields, sections, or subheadings beyond what is defined in the format.**
    - **Within paragraph sections (e.g., About the Company, Internship Overview), bold the important words listed above (e.g., company name, skills, keywords) using <b> tags to make them stand out. Do NOT bold words within <ul> lists, as they are already highlighted as bullet points.**
    - Ensure the response is at least {word_count} words. Expand each section thoughtfully with relevant details, examples, subpoints, and insights to reach the minimum word count, but do NOT add new sections or fields.
    - Make the tone and wording fit the nature of the role (e.g., formal for full-time, friendly for internships).
    - Do not add Package, Last Date to apply, and vacancies unless explicitly specified in the format.
    - Do not be brief. Elaborate on each section within the defined format, include real-world relevance or examples, and use rich descriptions or explanations wherever possible.
    - {"- Ensure the response is at least " + str(word_count) + " words. Expand each section thoughtfully with relevant details, examples, subpoints, and insights to reach the minimum word count." if force_elaboration else "- Keep it concise. Prioritize clarity and structure, but avoid unnecessary elaboration."}

Additional Info Provided by User:
{additional_info}
    """)

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(data)
    # Post-process the response to ensure tight spacing
    cleaned_response = clean_html_spacing(response)
    return cleaned_response