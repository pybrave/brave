import glob
import re
from functools import reduce

def glob_to_regex(glob_path: str) -> str:
    # 转义路径中的正则特殊字符（除了 *）
    escaped = re.escape(glob_path)
    # 把转义的 \* 替换成 (.+)
    regex = escaped.replace(r'\*', r'(.+)')
    return f'r"{regex}"'

def from_glob_get_file(content,dir=""):
    form_data = {}
    for k,v in content.items():
        pattern_str = f"{dir}/{v}"
        file_list = glob.glob(pattern_str)
        pattern = re.compile(glob_to_regex(pattern_str)[2:-1]) 
        result_dict = {}
        for file in file_list:
            match = pattern.match(file)
            if match:
                # match_dict = match.groupdict()
                file_name = match.group(1)
                result_dict[file_name] = file
        form_data[k] = result_dict
    common_samples = reduce(lambda  x,y: set(x.keys()) & set(y.keys()), form_data.values())
    result = []
    for name in  common_samples:
        result_dict = { "analysis_key":name}
        for k,files in  form_data.items():
            result_dict.update({
                k:files[name]
            })
        result.append(result_dict)

    return result