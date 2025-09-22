import re
import json
from shortuuid import uuid

# 原始文本列表
# lines = [
#     "AMetabolism",
#     "B  Global and overview maps",
#     "C    01100  Metabolic pathways",
#     "C    01110  Biosynthesis of secondary metabolites",
#     "C    01120  Microbial metabolism in diverse environments",
#     "C    01200  Carbon metabolism",
#     "C    01210  2-Oxocarboxylic acid metabolism",
#     "C    01212  Fatty acid metabolism",
#     "C    01230  Biosynthesis of amino acids",
#     "C    01232  Nucleotide metabolism",
#     "C    01250  Biosynthesis of nucleotide sugars",
#     "C    01240  Biosynthesis of cofactors",
#     "C    01220  Degradation of aromatic compounds",
#     "C    01310  Nitrogen cycle",
#     "C    01320  Sulfur cycle"
# ]

category = "KEGG"
last_parent = {}  # 保存每个层级最新的 tree_number
output = []

def generate_entity_id(code):
    return f"map{code}"

def parse_kegg_hierarchy(lines):
    output.append({
        "entity_name": "KEGG",
        "category": "KEGG",
        "entity_id": uuid(),
        "parent_tree": None,
        "tree_number": "KEGG"
    })
    for line in lines:
        line = line.strip()
        if not line:
            continue

        level = line[0]  # A/B/C
        content = line[1:].strip()

        node = {"category": category}

        if level == 'A':
            node["entity_name"] = content  # 根节点
            node["category"] = category
            node["parent_tree"] = category
            children_count = sum(1 for n in output if n.get("parent_tree") == category)
            tree_number = f"{category}.{children_count + 1:03d}"
            last_parent['A'] = tree_number
            node["entity_id"] = uuid()
            
        elif level == 'B':
            node["entity_name"] = content
            parent_tree = last_parent['A']
            node["parent_tree"] = parent_tree
            node["entity_id"] = uuid()
            # 生成 tree_number
            children_count = sum(1 for n in output if n.get("parent_tree") == parent_tree)
            tree_number = f"{parent_tree}.{children_count + 1:03d}"
            last_parent['B'] = tree_number
        elif level == 'C':
            # C 层可能带 code
            m = re.match(r"(\d{5})\s+(.*)", content)
            if m:
                code, name = m.groups()
                node["entity_name"] = name
                node["entity_id"] = generate_entity_id(code)
            else:
                node["entity_name"] = content
            parent_tree = last_parent['B']
            node["parent_tree"] = parent_tree
            children_count = sum(1 for n in output if n.get("parent_tree") == parent_tree)
            tree_number = f"{parent_tree}.{children_count + 1:03d}"
        node["tree_number"] = tree_number
        output.append(node)
    return output

    # 输出 JSON
# print(json.dumps(output, indent=2, ensure_ascii=False))
