import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai

from dotenv import load_dotenv
import os

load_dotenv()  # load variables from .env file into environment
api_key = os.getenv("GOOGLE_API_KEY")
api_token = os.getenv("JIRA_API_KEY")  # ✅ safer


email = 'vanshikaagarwal278@gmail.com'
domain = 'vanshikaagarwal278.atlassian.net'
project_key = 'TRAC' 

url = f"https://{domain}/rest/api/3/search"

query = {
    'jql': f'project = {project_key} AND issuetype = Story',
    'maxResults': 200,
    'fields': 'summary,description,status,assignee'
}

headers = {
    "Accept": "application/json"
}

auth = HTTPBasicAuth(email, api_token)


response = requests.get(url, headers=headers, params=query, auth=auth)


data = response.json()
if 'issues' not in data:
    print("No issues found in response")
    print(f"Response data: {data}")
    exit(1)

# Continue with the rest of your code

# --- GEMINI PART ---

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def extract_insights_from_story(story_text, description):
    prompt = f"""Analyze the following Jira user story: "{story_text}"
    The story is about a {description}.
    Extract the following:
    - Key Actions (in bullet points)
    - Intent (one line)
    - Expected Entities (in a list)
    while giving the answer don't give bracket words """

    response = model.generate_content(prompt)
    return response.text


# --- PROCESS AND PRINT STORIES ---

for issue in data['issues']:
    story_key = issue['key']
    summary = issue['fields']['summary']
    description = issue['fields'].get('description', 'No description provided')
    
    print(f"\nStory: {story_key} - {summary} \n\nDescription: {description}")
    result = extract_insights_from_story(summary, description)
    print(result)