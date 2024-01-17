import subprocess
import time
import git
import os

# Start the Python script.
process = subprocess.Popen(["python", "main.py", "--auto"])

# Check for GitHub updates every 1 minutes.
while True:
    # Check for updates.
    repo = git.Repo(os.getcwd())
    origin = repo.remotes.origin
    origin.fetch()
    if origin.refs[0].commit.hexsha != repo.head.commit.hexsha:
        # Gracefully terminate the Python script.
        process.terminate()
        process.wait()    
    
        # There are updates available.
        print("Updates available. Updating now...")
        repo.git.pull()

        # Get the commit details.
        commit_details = repo.git.log(n=1)

        # Print the commit details with the update notification.
        print("Update successful. Commit details:")
        print(commit_details)

        # Start the Python script again.
        process = subprocess.Popen(["python", "main.py", "--auto"])

    # Sleep for 1 minute.
    time.sleep(60)