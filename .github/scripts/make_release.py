import sys
from datetime import datetime

import github

_, tar_gz, version, access_key = sys.argv

git = github.Github(auth=github.Auth.Token(access_key))

defelement = git.get_repo("DefElement/DefElement")
branch = defelement.get_branch("main")
ref = defelement.get_git_ref("heads/main")

release = defelement.create_git_tag_and_release(
    f"v{version}",
    f"v{version}",
    f"v{version}",
    f"Snapshot of DefElement, {datetime.now().strftime('%d %B %Y')}.\n\nThis release is archived at [doi.org/10.5281/zenodo.17904468](https://doi.org/10.5281/zenodo.17904468)",
    branch.commit.sha,
    "commit",
)

for asset in release.get_assets():
    asset.delete_asset()

release.upload_asset(tar_gz)
