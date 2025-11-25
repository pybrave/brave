import glob
import re
from functools import reduce

from brave.api.config.config import get_settings

def glob_to_regex(glob_path: str) -> str:
    # 转义路径中的正则特殊字符（除了 *）
    escaped = re.escape(glob_path)
    # 把转义的 \* 替换成 (.+)
    regex = escaped.replace(r'\*', r'(.+)')
    return f'r"{regex}"'

def build_form_data(dir,form_data,settings,k,v):
    if dir : 
        pattern_str = f"{dir}/{v}".strip()
    else:
        pattern_str = v.strip()

    if pattern_str.startswith("~"):
        pattern_str = pattern_str.replace("~",str(settings.ANALYSIS_DIR))

    
    file_list = glob.glob(pattern_str)
    pattern = re.compile(glob_to_regex(pattern_str)[2:-1]) 
    result_dict = {}
    for file in file_list:
        match = pattern.match(file)
        if match:
            # match_dict = match.groupdict()
            file_name = match.group(1)
            result_dict[file_name] = file
    if result_dict:
        form_data[k] = result_dict
    
def from_glob_get_file(content,dir=None):
    settings = get_settings()
    form_data = {}
    for k,v in content.items():
        if isinstance(v,list):
            for item in v:
                build_form_data(dir,form_data,settings,k,item)
        else:
            build_form_data(dir,form_data,settings,k,v)
    # common_samples = reduce(lambda  x,y: set(x.keys()) & set(y.keys()), list(form_data.values()))
    # dicts = list(form_data.values())
    # common_samples = reduce(lambda x, y: set(x) & set(y), (d.keys() for d in dicts))
    result = []
    if form_data:
        common_samples =  set.intersection(*(set(d.keys()) for d in form_data.values()))
        
        for name in  common_samples:
            result_dict = { "sample_name":name}
            for k,files in  form_data.items():
                result_dict.update({
                    k:files[name]
                })
            result.append(result_dict)

    return result