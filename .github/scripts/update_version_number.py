import sys
from datetime import datetime

import github

version = datetime.now().strftime("%Y.%m")
branch = f"v{version}"

_, access_key = sys.argv

git = github.Github(access_key)

defelement = git.get_repo("DefElement/DefElement")
branch = defelement.get_branch("main")
ref = defelement.get_git_ref("heads/main")
base_tree = defelement.get_git_tree(branch.commit.sha)

pyproject_file = defelement.get_contents("pyproject.toml", branch.commit.sha)
pyproject = pyproject_file.decoded_content.decode("utf8")

pre_project, post_project = pyproject.split("[project]\n")
pre_version, post_version = pyproject.split("version = ")
post_version = post_version.split("\n", 1)[1]

new_branch = defelement.get_branch(branch)
defelement.update_file(
    "pyproject.toml",
    "Update version number",
    f'{pre_project}[project]\n{pre_version}version="{version}"\n{post_version}',
    sha=pyproject_file.sha,
    branch=branch,
)
pr = defelement.create_pull(title="Update version number", body="", base="main", head=branch)
pr.enable_automerge()

print(f"branch={branch}")
