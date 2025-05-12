import subprocess
import requests
import time

API_KEY = "AIzaSyAXfDBDNs6rPXzyHtEKHcR047ml7AySTMo"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def get_all_commit_hashes():
    result = subprocess.run(["git", "log", "--pretty=format:%H"], stdout=subprocess.PIPE, text=True)
    return result.stdout.strip().split("\n")

def get_commit_diff(commit_hash):
    result = subprocess.run(["git", "show", commit_hash, "--no-color"], stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def summarize_with_gemini(diff_text):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Review or summarize the following Git commit:\n\n{diff_text}"
                    }
                ]
            }
        ]
    }
    response = requests.post(f"{ENDPOINT}?key={API_KEY}", headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Error summarizing."

def main():
    commit_hashes = get_all_commit_hashes()
    print(f"📦 Found {len(commit_hashes)} commits.")

    for i, commit_hash in enumerate(reversed(commit_hashes), start=1):  # Oldest to newest
        print(f"\n🔄 [{i}/{len(commit_hashes)}] Commit {commit_hash}")
        diff = get_commit_diff(commit_hash)
        if len(diff) > 12000:
            print("⚠️ Commit too large, skipping or truncate manually.")
            continue
        summary = summarize_with_gemini(diff)
        print(f"🧠 Gemini Review:\n{summary}")
        time.sleep(1)  # Avoid rate limits

if __name__ == "__main__":
    main()
