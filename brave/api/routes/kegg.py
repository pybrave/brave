from fastapi import APIRouter
from Bio.KEGG.KGML.KGML_parser import read
import requests
import os
from lxml import etree

from brave.api.config.config import get_settings

kegg_api = APIRouter(prefix="/kegg")


def download_kgml(pathway_id: str) -> str:
    """Download KEGG KGML file"""
    settings = get_settings()
    kgml_path = f"{settings.DATABASES_DIR}/kegg/{pathway_id}/{pathway_id}.kgml"
    if not os.path.exists(kgml_path):
        os.makedirs(os.path.dirname(kgml_path), exist_ok=True)
        url = f"http://rest.kegg.jp/get/{pathway_id}/kgml"
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(kgml_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
        else:
            raise FileNotFoundError(f"Unable to fetch KGML file for {pathway_id}")
        

    img_path = f"{settings.DATABASES_DIR}/kegg/{pathway_id}/{pathway_id}.png"
    if not os.path.exists(img_path):
        tree = etree.parse(kgml_path)
        root = tree.getroot()
        img_url = root.attrib.get("image")
        # download image to img_path
        img_resp = requests.get(img_url)
        if img_resp.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(img_resp.content)
        else:
            raise FileNotFoundError(f"Unable to fetch image file for {pathway_id}")
    return kgml_path, img_path


@kegg_api.get("/pathway/{pathway_id}/markers")
def get_markers(pathway_id: str):
    up = {"C04549", "5337"}
    down = {"C00024"}
    kgml_path, img_path = download_kgml(pathway_id)

    with open(kgml_path) as f:
        p = read(f)

    markers = []
    for e in p.entries.values():
        if e.type == "compound" or e.type == "gene":
            for n in e.name.split():
                cid = n.split(":")[1]
                if cid in up:
                    graphics = e.graphics[0]
                    markers.append({"id": cid, "type":graphics.type,"radius":graphics.width/2,"x": graphics.x, "y": graphics.y, "width": graphics.width, "height": graphics.height ,"status": "up"})
                elif cid in down:
                    markers.append({"id": cid, "x": e.graphics.x, "y": e.graphics.y, "status": "down"})

    return markers



@kegg_api.get("/kgml/{pathway_id}")
def parse_kgml(pathway_id: str):
    kgml_path, img_path = download_kgml(pathway_id)
    # file_path = f"/ssd1/wy/workspace2/nextflow-fastapi/hsa04144.kgml"  # 存放KGML文件
    tree = etree.parse(kgml_path)
    root = tree.getroot()
    settings = get_settings()
    img_url =  img_path.replace(str(settings.DATABASES_DIR),"/brave-api/database-dir") 

    image = img_url # root.attrib.get("image")
    title = root.attrib.get("title")

    entries = []
    for entry in root.findall("entry"):
        eid = entry.attrib.get("id")
        name = entry.attrib.get("name")
        type_ = entry.attrib.get("type")
        link = entry.attrib.get("link")
        name = name.split()
        if type_=="compound":
            name = [item.replace("cpd:","") for item in name]
        elif type_ == "ortholog":
            name = [item.replace("ko:","") for item in name]
        elif type_ == "group":
            continue
        g = entry.find("graphics")
        if g is None:
            continue
        if g.attrib.get("type")=="line":
            continue
        x = float(g.attrib.get("x"))
        y = float(g.attrib.get("y"))
        w = float(g.attrib.get("width", 0))
        h = float(g.attrib.get("height", 0))
        label = g.attrib.get("name", "")
        entries.append({
            "id": eid,
            "name": name,
            "type": type_,
            "link": link,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "label": label,
        })

    return {
        "title": title,
        "image": image,
        "entries": entries
    }