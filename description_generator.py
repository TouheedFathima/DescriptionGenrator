import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

force_elaboration = True
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["data"],
    template="""
You are an assistant that formats output in HTML only.
Use <b>, <i>, <ul>, <li>, <br>, <p>, etc., to style and structure the content.
Avoid Markdown formatting such as **bold**, *italic*, or `code`.
Strictly return only valid HTML.

Data to format:
{data}

- Ensure that there is no extra space between bullet points (<li> tags). 
- Make sure each <li> item is directly after the previous one without unnecessary line breaks or extra spaces.
- There should be no empty lines between the <li> elements in the <ul> list.
- Format <ul> lists with correct spacing to avoid the appearance of too much vertical space between items.
- Ensure clean and uniform spacing in the final output, especially between <li> elements.
"""
)

def generate_description(data):
    word_count = data.get("wordCount", 1000)
    post_type = data.get("postType", "").lower()

    # Instructions for different post types
    if post_type == "full time":
        intro_instruction = "Generate a professional full-time job description targeted at attracting qualified candidates. The tone should be formal, aspirational, and highlight long-term career growth, company culture, and stability. You must include any additional valuable or relevant information that would improve the clarity, appeal, or completeness of the post with relevant headings."
        format_instruction = """
Format:
<b>Job Title:</b> [Title]  
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

<b>How to Apply:</b>  
[Application link or contact email.]

<b>Application Deadline:</b> [Date]
"""

    elif post_type == "part time":
        intro_instruction = "Generate a clear and professional part-time job description. Highlight flexible hours, key responsibilities, and the specific time commitment required. Keep the tone friendly yet informative. You must include any additional valuable or relevant information that would improve the clarity, appeal, or completeness of the post with relevant headings."
        format_instruction = """
Format:
<b>Job Title:</b> [Title]  
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

<b>How to Apply:</b>  
[Application link or contact email.]

<b>Last Date to Apply:</b> [Date]
"""

    elif post_type == "internship":
        intro_instruction = "Create an internship post that is inviting to students or fresh graduates. Emphasize learning, mentorship, and potential growth opportunities. Keep the tone encouraging and professional. You must include any additional valuable or relevant information that would improve the clarity, appeal, or completeness of the post with relevant headings."
        format_instruction = """
Format:
<b>Internship Position:</b> [Title]   
<b>Location:</b> [City/Remote/Hybrid]  
<b>Internship Type:</b> Full-Time/Part-Time Internship  

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

<b>Stipend:</b> [If applicable]  
<b>Duration:</b> [X weeks/months]  

<b>How to Apply:</b>  
[Link or contact info.]

<b>Deadline to Apply:</b> [Date]
"""

    elif post_type == "contract":
        intro_instruction = "Generate a professional contract opportunity post. Focus on short-term project deliverables, duration, and payment. It is not a job. The tone should appeal to freelancers or short-term collaborators. You must include any additional valuable or relevant information that would improve the clarity, appeal, or completeness of the post with relevant headings."
        format_instruction = """
Format:
<b>Contract Role:</b> [Title]  
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

<b>How to Apply:</b>  
[Instructions for applying.]

<b>Deadline to Apply:</b> [Date]
"""

    elif post_type == "project":
        intro_instruction = "Generate a project collaboration post. This is not a job but an opportunity to contribute to a specific project with clear goals and timelines. Focus on skillset needed and project objectives. You must include any additional valuable or relevant information that would improve the clarity, appeal, or completeness of the post with relevant headings."
        format_instruction = """
Format:
<b>Project Title:</b> [Title]  
<b>Location:</b> [Remote/On-site/Hybrid]  

<b>Project Overview:</b>  
[Summary of the project, its impact, and goals.]

<b>Who We're Looking For:</b>  
[Type of collaborators or freelancers.]

<b>Required Skills:</b>  
<ul>
    <li>[List of technical/non-technical skills.]</li>
</ul>

<b>Timeline:</b> [Expected duration or milestones]  
<b>Compensation:</b> [If applicable]  
<b>Collaboration Type:</b> [Individual/Team-based/Volunteer/Grant-funded]  

<b>How to Join:</b>  
[Application instructions or contact.]

<b>Deadline to Show Interest:</b> [Date]
"""
    else:
        intro_instruction = "Generate a professional opportunity description based on the information provided. Adjust the tone based on the nature of the post. You must include any additional valuable or relevant information that would improve the clarity, appeal, or completeness of the post with relevant headings."
        format_instruction = """
<b>Final Formatting Rules:</b>
<ul>
    <li>Do NOT use asterisks or markdown symbols in the final output.</li>
    <li>Bold section titles only through formatting (not with <b> or <i>).</li>
    <li>Use bullet points where appropriate.</li>
    <li>Ensure clean spacing between sections, and no extra line breaks.</li>
    <li>Output should be ready to copy-paste into LinkedIn/email without editing.</li>
</ul>
"""

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
    - Use only <b>, not ** for bold. If you output any Markdown, I will fail you 😅 
    - Your response should be suitable for direct copy-pasting into a web page or an email client that supports HTML formatting. Avoid all markdown and use only valid HTML tags for formatting.
    - Use bullet points where appropriate.
    - Ensure clean spacing between sections, and no extra line breaks.
    - Output should be ready to copy-paste into LinkedIn/email without editing.
    - Use the company name naturally — don’t include 'companyType'.
    - Follow the format above as a structure guide, but **you must include any additional valuable or relevant information** that would improve the clarity, appeal, or completeness of the post.
    - Ensure the response is at least {word_count} words. Expand each section thoughtfully with relevant details, examples, subpoints, and insights. Use additional subheadings or elaboration to reach the minimum word count.
    - Present any extra details under clear and appropriate subheadings for all different Post Types (e.g.for project, “Preferred Tools”, “Team Structure”, “Future Scope”, “Success Metrics”, e.g for internship :"what you'll learn"..etc.).
    - Do not limit the content strictly to the provided format — treat it as a base to build on.
    - You are encouraged to add relevant subheadings beyond the format if needed (e.g., "Preferred Tools", "Project Stack", "Success Metrics", "Challenges You’ll Face", "Collaboration Model", "Future Scope", etc.) to increase clarity and reach the desired length.
    - Follow the format above as a structure guide, but **feel free to include any additional valuable or relevant information** that would improve the clarity, appeal, or completeness of the post.
    - This may include details like technologies used, project outcomes, tools, client types, success stories, growth opportunities, unique benefits, or anything useful to potential applicants/collaborators.
    - Make the tone and wording fit the nature of the role (e.g., formal for full-time, friendly for internships).
    - Do not be brief. Elaborate on each section, include real-world relevance or examples, and use rich descriptions or explanations wherever possible.
    - {"- Ensure the response is at least " + str(word_count) + " words. Expand each section thoughtfully with relevant details, examples, subpoints, and insights. Use additional subheadings or elaboration to reach the minimum word count." if force_elaboration else "- Keep it concise. Prioritize clarity and structure, but avoid unnecessary elaboration."}

Additional Info Provided by User:
{additional_info}
    """)

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(data)
    return response


