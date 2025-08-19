import shutil
import os

def delete_all_in_dir(path):
    print(f"delete file: {path}")
    if not os.path.exists(path):
        print(f"{path} 不存在")
        return
    
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  # 删除文件或符号链接
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 删除文件夹及其内容
        except Exception as e:
            print(f"删除 {file_path} 失败: {e}")
