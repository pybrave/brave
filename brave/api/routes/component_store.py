import os
from fastapi import APIRouter
from brave.api.config.config import get_settings
import glob
import json
from collections import defaultdict
from brave.api.config.db import get_engine
from brave.api.schemas.component_store import ComponentStore, GetStoreRequest, RelationStore
import brave.api.service.pipeline as pipeline_service
import requests
import base64
from brave.api.service import store_service


component_store_api = APIRouter(prefix="/component-store",tags=["component_store"])

remote_stores = defaultdict(dict)

def open_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data["file_path"] = file_path
    
    return data

def list_local_components(store_name,relation_type):
    settings = get_settings()
    store_dir = settings.STORE_DIR
    # lock_file = f"{store_dir}/{store_name}.lock"
    # if os.path.exists(lock_file):
    #     with open(lock_file, 'r', encoding='utf-8') as f:
    #         lock_data = json.load(f)
    #     return {
    #         "data":[],
    #         "total":0,
    #         "lock_data":lock_data,
    #     }

    


      
    file_list = glob.glob(f"{store_dir}/{store_name}/{relation_type}/*/component_relation.json")
    file_list = [open_file(file) for file in file_list]
    relation_ids= [ item["relation_id"] for item in file_list]
    with get_engine().begin() as conn: 
        relation_installed =  pipeline_service.find_relation_list_in_ids(conn,relation_ids)

    installed_dict = { item["relation_id"]:item for item in relation_installed}
    for item in file_list:
        if item["relation_id"] in installed_dict:
            item["installed"] = True
        else:
            item["installed"] = False
        item["address"] ="local"
        if "img" in item and  item["img"] is not None and item["img"] !="":
            # img_dir = item["file_path"].replace(str(settings.STORE_DIR),"")
            # img_dir = os.path.dirname(img_dir)
            img_name=os.path.basename(item["img"])
            relation_type = item["relation_type"]
            relation_id = item["relation_id"]
            item["img"] = f"/brave-api/store-dir/{store_name}/{relation_type}/{relation_id}/{img_name}"
        else:
            item["img"] = f"/brave-api/img/pipeline.jpg"
    # result = {
    #     "data":file_list,
    #     "total":len(file_list)
    # }
    # config_file = f"{store_dir}/{store_name}/.config"
    # if os.path.exists(config_file):
    #     with open(config_file, 'r', encoding='utf-8') as f:
    #         config_data = json.load(f)
    #         if "git_url" in config_data:
    #             result["git_url"] = config_data["git_url"]

    return file_list

def format_store(file_path):
    filename = os.path.basename(file_path)
    if os.path.exists(f"{file_path}/main.json"):
        with open(f"{file_path}/main.json", 'r', encoding='utf-8') as f:
            try:
                name = json.load(f).get("name", filename)
            except:
                name = filename
    else:
        name = filename
    
    return {
        "store_name":os.path.basename(file_path),
        "store_path":file_path,
        "name":name,
        "address":"local"
    }

def list_local_store():
    settings = get_settings()
    store_dir = settings.STORE_DIR
    file_list = glob.glob(f"{store_dir}/*")
    file_list = [ format_store(file) for file in file_list if os.path.isdir(file) and "remote" not in  file  ] 
    return file_list

# @component_store_api.get("/list-stores")
# async def list_store(address:str):
#     if address=="github":
#         return [{
#                     "store_name":"quick-start-v2",
#                     "store_path":"pybrave",
#                     "name":"Quick Start Store V2",
#                     "address":"github"
#                 }]
#     else:
#         return list_local_store()



@component_store_api.post("/list-components")
async def list_components_by_type(componentStore:ComponentStore):
    if componentStore.address =="github":
        components = list_remote_components(componentStore.store_path,
                                            componentStore.store_name,
                                            componentStore.component_type,
                                            componentStore.remote_force,
                                            componentStore.branch,
                                            componentStore.token)
    elif componentStore.address =="local":
        components = list_local_components(componentStore.store_name,componentStore.component_type)
    else:
        raise ValueError("address must be 'local' or 'github'")
    return components

@component_store_api.post("/details-by-store-id/{store_id}")
async def list_components_by_type(store_id:str, type:str="tools"):
    with get_engine().begin() as conn: 
        store = store_service.find_store_by_id(conn,store_id)
    if not store:
        raise ValueError("Store not found")
    store = dict(store)

    store_name = store["path_name"]
    components = list_local_components(store_name, type)
    return {
        "store":store,
        "data":components,
    }



@component_store_api.post("/list-relations")
async def list_components_by_type(relationStore:RelationStore):
    if relationStore.address =="github":
        components = list_remote_components(relationStore.store_path,
                                            relationStore.store_name,
                                            relationStore.relation_type,
                                            relationStore.remote_force,
                                            relationStore.branch,
                                            relationStore.token)
    elif relationStore.address =="local":
        components = list_local_components(relationStore.store_name,relationStore.relation_type)
    else:
        raise ValueError("address must be 'local' or 'github'")
    return components

# git@github.com:pybrave/store-repo.git
@component_store_api.post("/get-remote-store")
async def get_remote_store(storeRequest:GetStoreRequest):
    owner = storeRequest.owner
    repo = storeRequest.repo
    file_path = storeRequest.file_path
    branch = storeRequest.branch
    token = storeRequest.token
    is_cache = storeRequest.is_cache
    
    settings = get_settings()
    store_dir = settings.STORE_DIR
    remote_cache = f"{store_dir}/remote/{owner}_{repo}.json"
    if os.path.exists(remote_cache) and  is_cache:
        with open(remote_cache, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Using cached data for {owner}/{repo} from {remote_cache}")
            return data
    
    if storeRequest.origin =="github":
        data = get_github_file_content(owner, repo, file_path, branch, token=token)
        data = json.loads(data)
            # Cache the data for future use
        os.makedirs(os.path.dirname(remote_cache), exist_ok=True)
        with open(remote_cache, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return data
    elif storeRequest.origin =="gitee":
        data = get_gitee_file_content(owner, repo, file_path, branch, token=token)
        data = json.loads(data)
            # Cache the data for future use
        os.makedirs(os.path.dirname(remote_cache), exist_ok=True)
        with open(remote_cache, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return data
    else:
        raise ValueError("origin must be 'github' or 'gitee'")


def list_remote_components(owner,store_name,relation_type,remote_force,branch,token):
    # data = get_github_file_content("pybrave","quick-start","main.json",branch="master")
    
    ## cache data
    settings = get_settings()
    store_dir = settings.STORE_DIR
    remote_cache = f"{store_dir}/remote/github/{owner}_{store_name}.json"
    if os.path.exists(remote_cache) and not remote_force:
        with open(remote_cache, 'r', encoding='utf-8') as f:
            data = f.read()
    else:
        data = get_github_file_content(owner,store_name,"main.json",branch,token=token)
        os.makedirs(os.path.dirname(remote_cache), exist_ok=True)
        with open(remote_cache, 'w', encoding='utf-8') as f:
            f.write(data)
    
    # data = get_github_file_content(owner,store_name,"main.json",branch,token=token)


    data = json.loads(data)
    if "relation" not in data:
        return []
    if relation_type not in data["relation"]:
        return []
    relations = data["relation"][relation_type]
    relation_ids= [ item["relation_id"] for item in relations]
    with get_engine().begin() as conn: 
        relation_installed =  pipeline_service.find_relation_list_in_ids(conn,relation_ids)
    installed_dict = { item["relation_id"]:item for item in relation_installed}
    for item in relations:
        relation_id = item["relation_id"]
        item["file_path"] = f"https://api.github.com/repos/{owner}/{store_name}/contents/{relation_type}/{relation_id}"
        item["branch"] = branch
        item["address"] ="github"
        item["name"]  = item.get("name",relation_id)
        if item["relation_id"] in installed_dict:
            item["installed"] = True
        else:
            item["installed"] = False
        if "img" in item and item["img"] !="":
            # img_name=item["img"]
            pass
        else:
            item["img"] = f"https://raw.githubusercontent.com/{owner}/{store_name}/refs/heads/{branch}/{relation_type}/{relation_id}/main.png"
    return relations

# https://api.github.com/repos/pybrave/quick-start/contents/software

def get_github_file_list(owner,repo,dir_path,branch="master"):
    import requests
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{dir_path}?ref={branch}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_gitee_file_content(owner, repo, path, branch="master", token=None):
    api_url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "content" in data and data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return content
        else:
            raise ValueError("Unable to decode file content from Gitee")
    else:
        raise ValueError(f"Failed to fetch file from Gitee: {response.status_code} - {response.text}")
    
    
def get_github_file_content(owner, repo, path, branch="main", token=None):
    meta_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    """
    Fetch the content of a file from a GitHub repository (handles large files automatically).
    
    :param owner: Repository owner, e.g. 'pybrave'
    :param repo: Repository name, e.g. 'quick-start'
    :param path: File path inside the repo, e.g. 'README.md'
    :param branch: Branch name, default is 'main'
    :param token: GitHub Personal Access Token (optional)
    :return: The decoded file content as a string
    """
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    # https://api.github.com/repos/pybrave/quick-start/contents/main.json?ref=main
    # https://api.github.com/repos/pybrave/quick-start/contents/main.json?ref=master
    # Step 1️⃣ Get file metadata (to retrieve SHA and size)
    
    meta_res = requests.get(meta_url, headers=headers)
    meta_res.raise_for_status()
    meta_data = meta_res.json()

    # Step 2️⃣ If the content is already returned (small files ≤ 1 MB)
    if "content" in meta_data and meta_data.get("encoding") == "base64":
        content = base64.b64decode(meta_data["content"]).decode("utf-8", errors="replace")
        return content

    # Step 3️⃣ For large files, use Git Data API to fetch blob by SHA
    sha = meta_data["sha"]
    blob_url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs/{sha}"
    blob_res = requests.get(blob_url, headers=headers)
    blob_res.raise_for_status()
    blob_data = blob_res.json()

    # Step 4️⃣ Decode Base64 content
    if blob_data.get("encoding") == "base64":
        content = base64.b64decode(blob_data["content"]).decode("utf-8", errors="replace")
        return content

    raise ValueError("Unable to decode file content")


