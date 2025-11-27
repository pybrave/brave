import glob
import os
from fastapi import APIRouter, HTTPException, Query
import asyncio
from fastapi.responses import FileResponse
from brave.api.schemas.file_operation import WriteFile
from collections import defaultdict
from pathlib import Path
from brave.api.config.config import get_settings
import pandas as pd
import json
import fitz  # PyMuPDF
import base64
from concurrent.futures import ThreadPoolExecutor
import threading
import copy
from brave.api.utils import oss_utils

from brave.api.utils import file_utils

# def pdf_page_to_base64(pdf_path, page_number=0, zoom=2):
#     """
#     读取 PDF 指定页并转为 base64 图片
#     :param pdf_path: PDF 文件路径
#     :param page_number: 页码 (从0开始)
#     :param zoom: 缩放倍率
#     :return: base64 字符串 (PNG)
#     """
#     doc = fitz.open(pdf_path)
#     page = doc.load_page(page_number)  # 页码从 0 开始
#     mat = fitz.Matrix(zoom, zoom)      # 放大，提高清晰度
#     pix = page.get_pixmap(matrix=mat)
#     img_bytes = pix.tobytes("png")

#     # 转 base64
#     base64_str = base64.b64encode(img_bytes).decode("utf-8")
#     return base64_str

def pdf_page_to_base64(pdf_path, page_number=0, zoom=2):
    try:
        doc = fitz.open(pdf_path)
        if page_number >= len(doc):
            raise ValueError(f"PDF 只有 {len(doc)} 页，无法加载第 {page_number} 页")

        page = doc.load_page(page_number)
        mat = fitz.Matrix(zoom, zoom)
        # pix = page.get_pixmap(matrix=mat)
        pix = page.get_pixmap(matrix=mat, alpha=False, clip=fitz.Rect(0, 0, 2000, 2000))

        img_bytes = pix.tobytes("png")
        return base64.b64encode(img_bytes).decode("utf-8")

    except Exception as e:
        # 任何错误返回 None 或占位图
        print(f"[ERROR] PDF 转图片失败: {pdf_path}, {e}")
        return None


def format_img_path(path):
    # print(f"Processing {path} in thread: {threading.current_thread().name}")
    settings = get_settings()
    base_dir = settings.ANALYSIS_DIR
    path_name = path.replace(str(base_dir),"")
    img_data = f"/brave-api/analysis-dir{path_name}"
    filename = os.path.basename(path)
    if  path.endswith(".download.pdf"):
        
        img_data = f"/brave-api/analysis-dir{path_name}".replace(".download.pdf",".png")
        filename = filename.replace(".download.pdf","")
        # pdf_file = "example.pdf"
        # b64 = pdf_page_to_base64(path, page_number=0, zoom=2)
        # img_data = f"data:image/png;base64,{b64}"
    elif path.endswith("pdf"):
        # pdf_file = "example.pdf"
        b64 = pdf_page_to_base64(path, page_number=0, zoom=2)
        img_data = f"data:image/png;base64,{b64}"
        filename = filename.replace(".pdf","")
    else:
        filename = filename.replace(".png","")
        # b64 = base64.b64encode(open(path
    # print("data:image/png;base64," + b64[:200] + "...")  # 打印前200字符
    # img_base64 = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
    return {
        "data":img_data,
        "type":"img",
        "filename":filename,
        "url":f"/brave-api/analysis-dir{path_name}"
    }

def format_table_output(path,row_num=None):
    # pd.set_option("display.max_rows", 1000)     # 最多显示 1000 行
    # pd.set_option("display.max_columns", 500)   # 最多显示 500 列
    data = ""
    data_type="table"
    order = 0
    if path.endswith("xlsx"):
        df =  pd.read_excel(path)
        data = file_utils.get_table_content_by_df(df)
        data_type="table"
    elif path.endswith("html") :
        # with open(path,"r") as f:
        #     data = f.read()
        data_type="html"
    elif path.endswith("sh") :
        with open(path,"r") as f:
            data = f.read()
        data_type="text"
    elif path.endswith(".download.tsv"):
        # df =  pd.read_csv(path,sep="\t", nrows=50).iloc[:, :30]
        # # df = pd.read_csv(path,sep="\t")
        # data = json.loads(df.to_json(orient="records")) 
        data=[]
        data_type="download"
    elif path.endswith("tsv"):
        df =  pd.read_csv(path,sep="\t")
        df = df.iloc[:, :100]
        # df = pd.read_csv(path,sep="\t")
        # data = json.loads(df.to_json(orient="records")) 
        data = file_utils.get_table_content_by_df(df,row_num)
        data_type="table"
    elif path.endswith(".vis"):
        data_type = os.path.basename(path).replace(".vis","")
        # df =  pd.read_csv(path,sep="\t", dtype={"pathwayId": str})
        # df = pd.read_csv(path,sep="\t")
        with open(path) as f:
            data = json.load(f)
        # data = json.loads(df.to_json(orient="records")) 
        # data_type="kegg_map"
    elif path.endswith(".diff"):
        with open(path,"r") as f:
            data = json.load(f)
        data_type="diff"
        order=11
    elif path.endswith("json"):
        with open(path,"r") as f:
            data = f.read()
        data_type="json"
    elif path.endswith(".feature.list"):
        with open(path,"r") as f:
            data = f.read()
        data_type="feature_list"
        order=9
    elif path.endswith("info"):
        with open(path,"r") as f:
            data = f.read()
        data_type="info"
        order=10
    else:
        with open(path,"r") as f:
            data = f.read()
        data_type="string"
      

    settings = get_settings()
    base_dir = settings.ANALYSIS_DIR
    file_name = path.replace(str(base_dir),"")
    return  {
        "data":data ,
        "order":order,
        "type":data_type,
        "filename":os.path.basename(path),
        "url":f"/brave-api/analysis-dir{file_name}"
    }
# def format_table_output(path):
#     with open(path,"r") as f:
#         text = f.read()
#     settings = get_settings()
#     base_dir = settings.BASE_DIR
#     file_name = path.replace(str(base_dir),"")
#     return  {
#         "data":text ,
#         "type":"table",
#         "url":f"/brave-api/dir{file_name}"
#     }

def format_html_output(path):
    settings = get_settings()
    base_dir = settings.ANALYSIS_DIR
    file_name = path.replace(str(base_dir),"")
    img_data = f"/brave-api/analysis-dir{file_name}"
    return {
        "data":img_data,
        "type":"img",
        "filename":os.path.basename(path),
        "url":f"/brave-api/analysis-dir{file_name}"
    }
async def visualization_results(path):
    # TEST
    # oss_utils.list_objects()

    path = f"{path}/output"
    images = []
    for ext in ("*.png", "*.jpg", "*.jpeg","*.pdf"):
        images.extend(glob.glob(os.path.join(path, ext)))

    html_list = []
    for ext in ("*.html",):
        html_list.extend(glob.glob(os.path.join(path, ext)))
    html_list = [format_html_output(html) for html in html_list]
    
   
    # images = [format_img_path(image) for image in images]
       # 多线程处理
    # with ThreadPoolExecutor(max_workers=8) as executor:
    #     images = list(executor.map(format_img_path, images))
    # print(f"Processing visualization_results in thread: {threading.current_thread().name}")

    tasks = [asyncio.to_thread(format_img_path, img) for img in images]
    images = await asyncio.gather(*tasks)
    grouped_images = defaultdict(list)
    for item in images:
        grouped_images[item["filename"]].append(item)

    merged_images = []
    for data_val, group in grouped_images.items():
        # 拷贝第一项作为基础
        merged_item = copy.deepcopy(group[0])
        merged_item["urls"] = [{ "format":os.path.splitext(g["url"])[1][1:],
                                "url":g["url"]} for g in group]
        merged_images.append(merged_item)
    # images = []
    tables = []
    for ext in ("*.csv", "*.tsv","*.txt", "*.xlsx","*.info","*.vis","*.feature.list","*.diff"):
        tables.extend(glob.glob(os.path.join(path, ext)))
    tables = [format_table_output(table,100) for table in tables]
    tables = sorted(tables, key=lambda x: x.get("order", 0), reverse=True)
    # textList = []
    # for ext in ("*.txt"):
    #     textList.extend(glob.glob(os.path.join(path, ext)))

    # textList = [format_text_output(text) for text in textList]

    return {
        "images": merged_images,
        "tables": tables,
        "htmls":html_list
    }
