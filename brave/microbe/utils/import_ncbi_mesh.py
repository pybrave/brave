import xml.etree.ElementTree as ET
import json
import pandas as pd
def get_json(file_path):
    # 解析 XML 文件
    tree = ET.parse("/ssd1/wy/workspace2/nextflow-fastapi/desc2025.xml")
    root = tree.getroot()

    mesh_json = []

    for descriptor in root.findall("DescriptorRecord"):
        # DescriptorUI
        ui_elem = descriptor.find("DescriptorUI")
        descriptor_ui = ui_elem.text if ui_elem is not None else None

        # DescriptorName
        name_elem = descriptor.find("DescriptorName/String")
        descriptor_name = name_elem.text if name_elem is not None else None
    # RegistryNumberList（新增）
        registry_numbers = []
        concept_elem = descriptor.find("ConceptList/Concept")
        if concept_elem is not None:
            reg_list_elem = concept_elem.find("RegistryNumberList")
            if reg_list_elem is not None:
                registry_numbers = [rn.text for rn in reg_list_elem.findall("RegistryNumber")]
        # TreeNumberList
        tree_numbers = []
        tree_list_elem = descriptor.find("TreeNumberList")
        if tree_list_elem is not None:
            tree_numbers = [tn.text for tn in tree_list_elem.findall("TreeNumber")]

        # PublicMeSHNote
        note_elem = descriptor.find("PublicMeSHNote")
        public_note = note_elem.text if note_elem is not None else None

        # PreviousIndexingList
        prev_indexing = []
        prev_list_elem = descriptor.find("PreviousIndexingList")
        if prev_list_elem is not None:
            prev_indexing = [pi.text for pi in prev_list_elem.findall("PreviousIndexing")]

        # 构建 JSON 对象
        descriptor_dict = {
            "DescriptorUI": descriptor_ui,
            "DescriptorName": descriptor_name,
            "TreeNumberList": tree_numbers,
            "PublicMeSHNote": public_note,
            "registry_numbers":registry_numbers,
            "PreviousIndexingList": prev_indexing
        }

        mesh_json.append(descriptor_dict)
    return mesh_json

