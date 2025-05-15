import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai

# Replace these
email = 'vanshikaagarwal278@gmail.com'
api_token = 'ATATT3xFfGF0aNvQkKdhgjmnGXSPS4k4jaZPh-q6nrVQxTJGJPfvaXXKvLs4HBiv9xTUtK0pI1GjV6jyZvuZMCb8rBLYHgBf9seagDqUvFXfowA0228yzttLEcg1niH3cKEVy1x5sRdgWID9gyY3VqZ1aOiESVSGxdljwFpgW6DlDxHaxc_beeY=65BF3C56'
domain = 'vanshikaagarwal278.atlassian.net'
project_key = 'TRAC' 

url = f"https://{domain}/rest/api/3/search"

query = {
    'jql': f'project = {project_key} AND issuetype = Story',
    'maxResults': 50,
    'fields': 'summary,status,assignee'
}

headers = {
    "Accept": "application/json"
}

auth = HTTPBasicAuth(email, api_token)

response = requests.get(url, headers=headers, params=query, auth=auth)

data = response.json()




# --- GEMINI PART ---

# Replace with your Gemini API key
genai.configure(api_key="AIzaSyAXfDBDNs6rPXzyHtEKHcR047ml7AySTMo")

model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def extract_insights_from_story(story_text):
    prompt = f"""Analyze the following Jira user story:

"{story_text}"


Extract the following:
- Key Actions (in bullet points)
- Intent (one line)
- Expected Entities (in a list)
while giving the answer don't give bracket words
"""

    response = model.generate_content(prompt)
    return response.text


# --- PROCESS AND PRINT STORIES ---

for issue in data['issues']:
    story_key = issue['key']
    summary = issue['fields']['summary']
    
    print(f"\nStory: {story_key} - {summary}")
    result = extract_insights_from_story(summary)
    print(result)