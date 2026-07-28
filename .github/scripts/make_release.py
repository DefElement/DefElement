import os
from datetime import datetime, timedelta, timezone

import github

access_key = os.environ.get("GITHUB_TOKEN", None)
version = os.environ.get("VERSION", None)
tar_gz = f"defelement-v{version}.tar.gz"
if "PATH" in os.environ:
    tar_gz = os.path.join(os.environ["PATH"], tar_gz)

git = github.Github(auth=github.Auth.Token(access_key))

defelement = git.get_repo("DefElement/DefElement")
main_branch = defelement.get_branch("main")
ref = defelement.get_git_ref("heads/main")

release = defelement.create_git_tag_and_release(
    f"v{version}",
    f"v{version}",
    f"v{version}",
    f"Snapshot of DefElement, {datetime.now(tz=timezone(timedelta())).strftime('%d %B %Y')}.\n\nThis release is archived at [doi.org/10.5281/zenodo.17904468](https://doi.org/10.5281/zenodo.17904468)",
    main_branch.commit.sha,
    "commit",
)

for asset in release.get_assets():
    asset.delete_asset()

release.upload_asset(tar_gz)
