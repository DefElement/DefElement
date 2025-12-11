import sys
from datetime import datetime

import github

_, tar_gz, version, access_key = sys.argv

assert version != "2025.09"  # Prevent release when initally merging

git = github.Github(access_key)

defelement = git.get_repo("DefElement/DefElement")
branch = defelement.get_branch("main")
ref = defelement.get_git_ref("heads/main")

release = defelement.create_git_tag_and_release(
    f"v{version}",
    f"v{version}",
    f"v{version}",
    f"Snapshot of DefElement, {datetime.now().strftime('%d %B %Y')}",
    branch.commit.sha,
    "commit",
)

for asset in release.get_assets():
    asset.delete_asset()

release.upload_asset(tar_gz)
