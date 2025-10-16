import requests
import os
import base64

def download_github_folder(api_url, target_dir, token=None):
    """
    Recursively download all files from a GitHub repository folder via the GitHub API.
    It first tries to decode Base64 'content' directly (if available) to reduce network calls.

    Args:
        api_url (str): GitHub API 'contents' endpoint for a folder.
        target_dir (str): Local directory to save files.
        token (str, optional): GitHub personal access token.
    """
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'

    # Step 1️⃣ Fetch the folder or file info
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        # raise Exception(f"Failed to fetch {api_url}: {response.status_code} {response.text}")
        print(f"⚠️ Warning: Failed to fetch {api_url}: {response.status_code} {response.text}")
        return

    items = response.json()

    # If a single file is returned, wrap it in a list
    if isinstance(items, dict):
        items = [items]

    # Step 2️⃣ Iterate over each item in the folder
    for item in items:
        item_type = item.get('type')
        item_name = item.get('name')
        item_path = os.path.join(target_dir, item_name)

        if item_type == 'file':
            print(f"📄 Downloading file: {item['path']}")
            os.makedirs(target_dir, exist_ok=True)

            # Try to decode Base64 content directly (GitHub may include it for small files)
            content = None
            if 'content' in item and item.get('encoding') == 'base64':
                try:
                    content = base64.b64decode(item['content'])
                except Exception as e:
                    print(f"⚠️ Failed to decode base64 for {item_name}: {e}")

            # If not present, fetch the content explicitly from API
            if content is None:
                file_res = requests.get(item['url'], headers=headers)
                file_res.raise_for_status()
                file_data = file_res.json()
                if 'content' in file_data and file_data.get('encoding') == 'base64':
                    content = base64.b64decode(file_data['content'])
                else:
                    # Fall back to download_url if no base64 content
                    raw_res = requests.get(item['download_url'], headers=headers)
                    raw_res.raise_for_status()
                    content = raw_res.content

            # Save file locally
            with open(item_path, 'wb') as f:
                f.write(content)

        elif item_type == 'dir':
            print(f"📁 Entering directory: {item['path']}")
            download_github_folder(item['url'], item_path, token)

        else:
            print(f"⚠️ Unknown item type: {item_type} ({item['path']})")
# def download_github_folder(api_url, target_dir, token=None):
#     """
#     Recursively download all files from a GitHub repository folder via the GitHub API.
    
#     Args:
#         api_url (str): GitHub API 'contents' endpoint for a folder.
#         target_dir (str): Local path to save downloaded files.
#         token (str, optional): GitHub personal access token (recommended for large repos or private repos).
#     """
#     headers = {}
#     if token:
#         headers['Authorization'] = f'token {token}'
    
#     # Fetch the folder contents
#     response = requests.get(api_url, headers=headers)
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch {api_url}: {response.status_code} {response.text}")

#     items = response.json()
    
#     # If the response is a single file, convert to a list
#     if isinstance(items, dict):
#         items = [items]

#     for item in items:
#         item_type = item['type']
#         item_name = item['name']
#         item_path = os.path.join(target_dir, item_name)

#         if item_type == 'file':
#             # Download file
#             print(f"Downloading: {item['path']}")
#             file_data = requests.get(item['download_url'], headers=headers)
#             os.makedirs(target_dir, exist_ok=True)
#             with open(item_path, 'wb') as f:
#                 f.write(file_data.content)
        
#         elif item_type == 'dir':
#             # Recursively download subfolder
#             print(f"Entering directory: {item['path']}")
#             download_github_folder(item['url'], item_path, token)



def get_github_file_content_by_url(meta_url, token=None):
    # meta_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
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
    # sha = meta_data["sha"]
    # blob_url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs/{sha}"
    # blob_res = requests.get(blob_url, headers=headers)
    # blob_res.raise_for_status()
    # blob_data = blob_res.json()

    # # Step 4️⃣ Decode Base64 content
    # if blob_data.get("encoding") == "base64":
    #     content = base64.b64decode(blob_data["content"]).decode("utf-8", errors="replace")
    #     return content

    raise ValueError("Unable to decode file content")
