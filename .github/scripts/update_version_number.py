import sys
from datetime import datetime

import github

version = datetime.now().strftime("%Y.%m")
branch_name = f"v{version}"

_, access_key = sys.argv

git = github.Github(auth=github.Auth.Token(access_key))

defelement = git.get_repo("DefElement/DefElement")
main_branch = defelement.get_branch("main")
ref = defelement.get_git_ref("heads/main")
base_tree = defelement.get_git_tree(main_branch.commit.sha)

defelement.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
new_branch = defelement.get_branch(branch_name)

# Update pyproject.toml
pyproject_file = defelement.get_contents("pyproject.toml", branch.commit.sha)
pyproject = pyproject_file.decoded_content.decode("utf8")
pre_project, post_project = pyproject.split("[project]\n")
pre_version, post_version = post_project.split("version = ")
post_version = post_version.split("\n", 1)[1]
pyproject = f'{pre_project}[project]\n{pre_version}version = "{version}"\n{post_version}'
defelement.update_file(
    "pyproject.toml",
    "[AUTOMATED] Update version number",
    pyproject,
    sha=pyproject_file.sha,
    branch=branch_name,
)

# Update .zenodo.json
zenodo_file = defelement.get_contents(".zenodo.json", branch.commit.sha)
zenodo = zenodo_file.decoded_content.decode("utf8")
pre_version, post_version = post_project.split('"version": "')
post_version = post_version.split('"', 1)[1]
zenodo = f'{pre_version}"version": "{version}"\n{post_version}'
pre_pubdate, post_pubdate = zenodo.split('"publication_date": "')
post_pubdate = post_pubdate.split('"', 1)[1]
zenodo = f'{pre_pubdate}"publication_date": "{datetime.now().strftime("%Y-%m-%d")}"\n{post_pubdate}'
defelement.update_file(
    ".zenodo.json",
    "[AUTOMATED] Update version number",
    zenodo,
    sha=zenodo_file.sha,
    branch=branch_name,
)

pr = defelement.create_pull(
    title="[AUTOMATED] Update version number", body="", base="main", head=branch_name
)
pr.enable_automerge("SQUASH")

print(f"branch={branch_name}")
