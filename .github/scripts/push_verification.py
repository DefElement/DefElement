import os
import sys

import github

access_key = os.environ.get("GITHUB_TOKEN", None)
_, path = sys.argv

git = github.Github(auth=github.Auth.Token(access_key))

defelement = git.get_repo("DefElement/DefElement")
branch = defelement.get_branch("verification")

with open(os.path.join(path, "verification.json")) as f:
    new_verification = f.read()
with open(os.path.join(path, "verification-history.json")) as f:
    new_verification_history = f.read()

old_verification = defelement.get_contents("verification.json", branch.commit.sha)
defelement.update_file(
    "verification.json",
    "verification.json",
    new_verification,
    old_verification.sha,
    branch="verification",
)

old_verification_history = branch.get_contents("verification-history.json")
old_verification_history = defelement.get_contents("verification-history.json", branch.commit.sha)
defelement.update_file(
    "verification-history.json",
    "verification-history.json",
    new_verification_history,
    old_verification_history.sha,
    branch="verification",
)
