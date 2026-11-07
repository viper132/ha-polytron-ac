"""Maintainer diagnostic and issue checker for Polytron Smart AC integration."""
import subprocess
import urllib.request
import json
import os
import sys

REPO = "viper132/ha-polytron-ac"
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", ".maintainer_state.json")

def get_github_token() -> str:
    """Retrieve GitHub token dynamically via Git Credential Manager."""
    try:
        proc = subprocess.Popen(
            ["git", "credential", "fill"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, _ = proc.communicate(input="protocol=https\nhost=github.com\n\n")
        for line in stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return os.environ.get("GITHUB_TOKEN", "")

def fetch_json(url: str, token: str) -> dict | list:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "viper132-maintainer-bot",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def check_repo_health():
    token = get_github_token()
    
    # 1. Fetch repo metadata
    repo_data = fetch_json(f"https://api.github.com/repos/{REPO}", token)
    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)
    open_issues_count = repo_data.get("open_issues_count", 0)

    # 2. Fetch open issues and pull requests
    issues = fetch_json(f"https://api.github.com/repos/{REPO}/issues?state=open", token)
    
    # 3. Read previous state
    prev_state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                prev_state = json.load(f)
        except Exception:
            pass

    last_seen_ids = set(prev_state.get("seen_ids", []))
    
    new_issues = []
    current_ids = []

    for item in issues:
        item_id = item.get("id")
        current_ids.append(item_id)
        is_pr = "pull_request" in item
        
        if item_id not in last_seen_ids:
            new_issues.append({
                "number": item.get("number"),
                "title": item.get("title"),
                "author": item.get("user", {}).get("login"),
                "type": "Pull Request" if is_pr else "Issue",
                "html_url": item.get("html_url"),
                "created_at": item.get("created_at"),
                "body": item.get("body", "")[:300] + ("..." if len(item.get("body", "")) > 300 else ""),
            })

    # Save updated state
    with open(STATE_FILE, "w") as f:
        json.dump({"seen_ids": current_ids, "last_check": str(repo_data.get("updated_at"))}, f, indent=2)

    # Output formatted report
    report = {
        "repo": REPO,
        "stars": stars,
        "forks": forks,
        "open_total": open_issues_count,
        "new_count": len(new_issues),
        "new_items": new_issues,
        "all_open": [
            {
                "number": i.get("number"),
                "title": i.get("title"),
                "author": i.get("user", {}).get("login"),
                "type": "Pull Request" if "pull_request" in i else "Issue",
                "html_url": i.get("html_url"),
            }
            for i in issues
        ]
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    check_repo_health()
