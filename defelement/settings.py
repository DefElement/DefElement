"""DefElement settings."""

import os as _os
import typing as _typing

import yaml as _yaml
from webtools import settings

dir_path = _os.path.join(_os.path.dirname(_os.path.realpath(__file__)), "..")
element_path = _os.path.join(dir_path, "elements")
template_path = _os.path.join(dir_path, "templates")
files_path = _os.path.join(dir_path, "files")
pages_path = _os.path.join(dir_path, "pages")
data_path = _os.path.join(dir_path, "data")
img_path = _os.path.join(dir_path, "img")

html_path = _os.path.join(dir_path, "_html")
htmlelement_path = _os.path.join(html_path, "elements")
htmlimg_path = _os.path.join(html_path, "img")
htmlindices_path = _os.path.join(html_path, "lists")
htmlfamilies_path = _os.path.join(html_path, "families")

verification_json = _os.path.join(dir_path, "verification.json")

github_token: _typing.Optional[str] = None

processes = 1

owners = ["mscroggs"]
with open(_os.path.join(data_path, "editors")) as f:
    editors = _yaml.load(f, Loader=_yaml.FullLoader)
with open(_os.path.join(data_path, "contributors")) as f:
    contributors = _yaml.load(f, Loader=_yaml.FullLoader)

url = "https://defelement.org"
website_name: _typing.List[_typing.Optional[str]] = ["DefElement", "DefElement"]
repo = "DefElement/DefElement"

settings.dir_path = dir_path
settings.html_path = html_path
settings.template_path = template_path
settings.github_token = github_token
settings.owners = owners
settings.editors = editors
settings.contributors = contributors
settings.url = url
settings.website_name = website_name
settings.repo = repo


def set_html_path(path: str):
    """Set HTML path."""
    global html_path
    global htmlelement_path
    global htmlimg_path
    global htmlindices_path
    global htmlfamilies_path
    html_path = path
    htmlelement_path = _os.path.join(path, "elements")
    htmlimg_path = _os.path.join(path, "img")
    htmlindices_path = _os.path.join(path, "lists")
    htmlfamilies_path = _os.path.join(path, "families")

    settings.html_path = path


def set_processes(n: int):
    """Set number of processes."""
    global processes
    processes = n


def set_github_token(token):
    """Set GitHub token."""
    global github_token
    github_token = token
    settings.github_token = token


def set_verification_json(vj: str):
    """Set path of verification JSON."""
    global verification_json
    verification_json = vj
