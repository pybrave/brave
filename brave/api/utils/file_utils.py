import json
import shutil
import os

import pandas as pd

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

def get_table_content(path,row_num=None):
    df_content_0 = pd.read_csv(path,sep="\t")
    return get_table_content_by_df(df_content_0,row_num)

def get_table_content_by_df(df_content,row_num=None):
    if row_num and row_num !=-1:
        df_content = df_content.head(int(row_num))
    tables = json.loads(df_content.to_json(orient="values"))
    columns = df_content.columns.tolist()
    tables.insert(0, columns)

    return  {
        "nrow":len(df_content),
        "ncol":len(columns),
        "tables":tables
    }
