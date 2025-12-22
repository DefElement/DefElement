import sys
import os
import json
import requests

_, file, token = sys.argv

doi = "10.5081/zenodo.17904468"
api_url = "zenodo.org"
# api_url = "sandbox.zenodo.org"

headers = {"Authorization": f"Bearer {token}"}
filename = file.split("/")[-1]
root_dir = os.path.join(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."),
    "..",
)

with open(os.path.join(root_dir, ".zenodo.json")) as f:
    metadata = json.load(f)


def post(url, **params):
    print(f"POST {url}")
    r = requests.post(url, params=params, headers=headers).json()
    print(r)
    return r


def get(url, **params):
    print(f"GET {url}")
    r = requests.get(url, params=params, headers=headers).json()
    print(r)
    return r


def put(url, data=None, content_type=None, **params):
    print(f"PUT {url}")
    if content_type is None:
        put_headers = headers
    else:
        put_headers = {**headers, "Content-Type": content_type}
    r = requests.put(url, data=data, params=params, headers=put_headers).json()
    print(r)
    return r


def delete(url, **params):
    print(f"DELETE {url}")
    r = requests.delete(url, params=params, headers=headers)
    print(r)
    return r


r = get(f"https://{api_url}/api/records", q=f"conceptdoi:{doi}")
id = r["hits"]["hits"][0]["id"]

r = get(f"https://{api_url}/api/deposit/depositions/{id}")
newversion_link = r["links"]["newversion"]

r = post(newversion_link)
new_id = r["links"]["latest_draft"].split("/")[-1]
bucket_link = r["links"]["bucket"]

for f in r["files"]:
    delete(f["links"]["self"])

r = put(
    f"https://{api_url}/api/deposit/depositions/{new_id}",
    json.dumps(metadata),
    "application/json",
)

with open(file, "rb") as f:
    r = put(f"{bucket_link}/{filename}", f)

r = post(f"https://{api_url}/api/deposit/depositions/{new_id}/actions/publish")

assert r["state"] == "done"
