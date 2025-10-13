import gradio as gr
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Your GitHub username and private repository name
GITHUB_OWNER = "akv-dev"  # Replace with your GitHub username
GITHUB_REPO = "spf-converter"  # Replace with your private repository name

# Get your Personal Access Token from an environment variable for security
# It is highly recommended to set this as an environment variable
# export GITHUB_TOKEN="your_personal_access_token_here"
# OR set GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxx" in a .env file and load it
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# API endpoint URL
GITHUB_API_URL = os.environ.get("GITHUB_API_URL", f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}")

# Headers for authenticated requests
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_branches():
    """Fetches all branches from the repository using the GitHub API."""
    if not GITHUB_TOKEN:
        return ["Error: GitHub token not found. Set the GITHUB_TOKEN environment variable."]

    branches_url = f"{GITHUB_API_URL}/branches"
    response = requests.get(branches_url, headers=HEADERS)
    
    if response.status_code == 200:
        branches = [branch['name'] for branch in response.json()]
        return branches
    else:
        return [f"Error ({response.status_code}): Could not fetch branches. Check your token and repo name."]

def get_commits(branch_name):
    """Fetches and formats commit history for a specific branch."""
    if "Error" in branch_name:
        return branch_name
    
    commits_url = f"{GITHUB_API_URL}/commits?sha={branch_name}"
    response = requests.get(commits_url, headers=HEADERS)

    if response.status_code == 200:
        commits = response.json()
        if not commits:
            return "No commits found for this branch."

        commit_history_text = "### Commit History for Branch: **`" + branch_name + "`**\n\n"
        for commit in commits[:10]: # Limiting to 10 commits for a clean UI
            sha = commit['sha'][:7]
            message = commit['commit']['message'].split('\n')[0]
            author = commit['commit']['author']['name']
            date = commit['commit']['author']['date']
            commit_history_text += f"- **`{sha}`** by `{author}` on `{date[:10]}`: {message}\n"

        return commit_history_text
    else:
        return f"Error ({response.status_code}): Could not fetch commits for branch '{branch_name}'. Check your token and repo name."

# Get the list of branches to populate the dropdown
branches_list = get_branches()

# Define the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown(
        f"# Git Commit Viewer for `{GITHUB_OWNER}/{GITHUB_REPO}`"
    )
    gr.Markdown(
        "Select a branch to view its commit history."
    )
    
    # Create the components
    branch_dropdown = gr.Dropdown(
        choices=branches_list,
        label="Select Branch",
        interactive=True
    )
    
    commit_history_output = gr.Markdown(
        label="Commit History"
    )

    # Link the components: when a branch is selected, update the commit history
    branch_dropdown.change(
        fn=get_commits,
        inputs=branch_dropdown,
        outputs=commit_history_output
    )

# Launch the app
demo.launch()