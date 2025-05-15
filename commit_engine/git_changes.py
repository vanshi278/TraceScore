from git import Repo, InvalidGitRepositoryError
import sys
import os
import google.generativeai as genai
from datetime import datetime

# --- CONFIG ---
REPO_PATH = "/Users/vanshikaagarwal/Desktop/Coding/TestingTraceScore"
DEVELOPER = "vanshikaagarwal278@gmail.com"
GEMINI_API_KEY = "AIzaSyAXfDBDNs6rPXzyHtEKHcR047ml7AySTMo"

def setup_gemini():
    """Configure Gemini API"""
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

def get_commit_changes(commit):
    """Get list of changed files and their contents from a commit"""
    if commit.parents:
        diffs = commit.parents[0].diff(commit)
    else:
        diffs = commit.diff(None)
    
    changed_files = []
    for diff in diffs:
        try:
            if diff.b_blob:
                content = diff.b_blob.data_stream.read().decode('utf-8')
                changed_files.append(f"\nFile: {diff.a_path}\n{content}")
                # Print for user feedback
                print(f"\nFile: {diff.a_path}")
                print("-" * 40)
                print(content)
                print("-" * 40)
        except UnicodeDecodeError:
            changed_files.append(f"\nFile: {diff.a_path}\n(Binary file)")
            print(f"\nFile: {diff.a_path}\n(Binary file)")
    
    return changed_files

def analyze_commit(model, commit_data):
    """Get AI analysis of commit changes"""
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
    """
    return model.generate_content(prompt).text

def main():
    try:
        # Initialize repository and Gemini
        repo = Repo(REPO_PATH)
        model = setup_gemini()
        
        # Get latest commit
        latest_commit = repo.head.commit
        
        if not (latest_commit.author.email.lower() == DEVELOPER.lower() or 
                latest_commit.author.name.lower() == DEVELOPER.lower()):
            print(f"Latest commit was not made by {DEVELOPER}")
            return
        
        # Print commit information
        print(f"\nAnalyzing latest commit:\n")
        print(f"Commit: {latest_commit.hexsha}")
        print(f"Author: {latest_commit.author.name} <{latest_commit.author.email}>")
        print(f"Date: {latest_commit.committed_datetime}")
        print(f"Message: {latest_commit.message.strip()}")
        print("\nChanged files:")
        print("=" * 80)
        
        # Get changed files
        changed_files = get_commit_changes(latest_commit)
        
        # Prepare data for analysis
        commit_data = {
            'hash': latest_commit.hexsha,
            'date': latest_commit.committed_datetime,
            'message': latest_commit.message.strip(),
            'files_content': changed_files
        }
        
        # Get and print AI analysis
        print("\nGemini Analysis:")
        print("=" * 80)
        print(analyze_commit(model, commit_data))
        print("=" * 80)

    except InvalidGitRepositoryError:
        print(f"Error: '{REPO_PATH}' is not a valid Git repository")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
