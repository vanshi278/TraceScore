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
    
    # Get the latest commit
    latest_commit = next(repo.iter_commits())
    
    if (latest_commit.author.email.lower() == DEVELOPER.lower() or 
        latest_commit.author.name.lower() == DEVELOPER.lower()):
        
        print(f"\nAnalyzing latest commit:\n")
        
        # Print detailed commit information
        print(f"Commit: {latest_commit.hexsha}")
        print(f"Author: {latest_commit.author.name} <{latest_commit.author.email}>")
        print(f"Date: {latest_commit.committed_datetime}")
        print(f"Message: {latest_commit.message.strip()}")
        print("\nChanged files:")
        print("=" * 80)
        
        # Get the list of changed files and their contents
        if latest_commit.parents:
            diffs = latest_commit.diff(latest_commit.parents[0])
        else:
            diffs = latest_commit.diff(None)
            
        # Prepare commit data for Gemini analysis
        commit_data = {
            'hash': latest_commit.hexsha,
            'date': latest_commit.committed_datetime,
            'message': latest_commit.message.strip(),
            'files_content': []
        }
        
        # Get changed files content
        for diff in diffs:
            print(f"\nFile: {diff.a_path}")
            print("-" * 40)
            try:
                if diff.b_blob:
                    content = diff.b_blob.data_stream.read().decode('utf-8')
                    print(content)
                    commit_data['files_content'].append(f"\nFile: {diff.a_path}\n{content}")
            except UnicodeDecodeError:
                print("(Binary file)")
                commit_data['files_content'].append(f"\nFile: {diff.a_path}\n(Binary file)")
            print("-" * 40)
        
        # Get and print summary from Gemini
        print("\nGemini Analysis:")
        print("=" * 80)
        print(get_code_summary(commit_data))
        print("=" * 80)
    else:
        print(f"Latest commit was not made by {DEVELOPER}")

except InvalidGitRepositoryError:
    print(f"Error: '{REPO_PATH}' is not a valid Git repository")
except Exception as e:
    print(f"An error occurred: {e}")
