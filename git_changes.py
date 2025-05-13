from git import Repo, InvalidGitRepositoryError
import sys
import os
import google.generativeai as genai
from datetime import datetime

# --- CONFIG ---
REPO_PATH = "/Users/vanshikaagarwal/Desktop/Coding/TestingTraceScore"
DEVELOPER = "vanshikaagarwal278@gmail.com"
GEMINI_API_KEY = "AIzaSyAXfDBDNs6rPXzyHtEKHcR047ml7AySTMo"  # Replace with your Gemini API key

def get_code_summary(commit_data):
    """Get summary of code changes using Gemini API"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = f"""
    Analyze this git commit and summarize the changes:
    Commit: {commit_data['hash']}
    Date: {commit_data['date']}
    Message: {commit_data['message']}
    
    Changed files and their contents:
    {commit_data['files_content']}
    
    Please provide:
    1. A brief summary of the changes
    2. Key modifications made
    3. Potential impact of changes
    """
    
    response = model.generate_content(prompt)
    return response.text

try:
    repo = Repo(REPO_PATH)
    
    print(f"\nAnalyzing commits by {DEVELOPER}:\n")
    found_commits = False
    
    for commit in repo.iter_commits():
        if (commit.author.email.lower() == DEVELOPER.lower() or 
            commit.author.name.lower() == DEVELOPER.lower()):
            found_commits = True
            
            # Print detailed commit information
            print(f"\nCommit: {commit.hexsha}")
            print(f"Author: {commit.author.name} <{commit.author.email}>")
            print(f"Date: {commit.committed_datetime}")
            print(f"Message: {commit.message.strip()}")
            print("\nChanged files:")
            print("=" * 80)
            
            # Get the list of changed files and their contents
            if commit.parents:
                diffs = commit.diff(commit.parents[0])
            else:
                diffs = commit.diff(None)
                
            for diff in diffs:
                print(f"\nFile: {diff.a_path}")
                print("-" * 40)
                try:
                    if diff.b_blob:
                        content = diff.b_blob.data_stream.read().decode('utf-8')
                        print(content)
                except UnicodeDecodeError:
                    print("(Binary file)")
                print("-" * 40)
            
            # Prepare commit data for Gemini analysis
            commit_data = {
                'hash': commit.hexsha,
                'date': commit.committed_datetime,
                'message': commit.message.strip(),
                'files_content': []
            }
            
            # Get all files in the commit's tree for analysis
            for item in commit.tree.traverse():
                if item.type == 'blob':
                    try:
                        content = item.data_stream.read().decode('utf-8')
                        commit_data['files_content'].append(f"\nFile: {item.path}\n{content}")
                    except UnicodeDecodeError:
                        commit_data['files_content'].append(f"\nFile: {item.path}\n(Binary file)")
            
            # Get and print summary from Gemini
            print("\nGemini Analysis:")
            print("=" * 80)
            print(get_code_summary(commit_data))
            print("=" * 80)

    if not found_commits:
        print(f"No commits found by {DEVELOPER}")

except InvalidGitRepositoryError:
    print(f"Error: '{REPO_PATH}' is not a valid Git repository")
except Exception as e:
    print(f"An error occurred: {e}")
