from fastapi import HTTPException


def get_path_name_from_url(url:str):
    url_lists = url.split("/")
    if len(url_lists) < 2:
        raise HTTPException(status_code=400, detail=f"Invalid git url: {url}")
    
    filename = url_lists[-1]
    # target_path is owner/repo
    url_path = url_lists[-2:]
    path_name = f"{url_path[0]}/{filename.replace('.git','')}"
    return path_name,filename

def build_publish_urls(path_name):
    
    publish_urls = [
        {
            "name": "github",
            "ssh": f"git@github.com:{path_name}.git",
            "https": f"https://github.com/{path_name}.git"
        }, {
            "name": "gitee",
            "ssh": f"git@gitee.com:{path_name}.git",
            "https": f"https://gitee.com/{path_name}.git"   
        }
    ]
    return publish_urls