import nbformat as nbf
from fastapi import APIRouter

norbook_api = APIRouter()

@norbook_api.get("/generate_notebook")
async def generate_notebook():
    nb = nbf.v4.new_notebook()

    cells = [
        nbf.v4.new_markdown_cell("# 自动生成的 Notebook\n这里写一些说明"),
        nbf.v4.new_code_cell("import sys\nprint(sys.argv)"),
        nbf.v4.new_code_cell("print('Hello from generated notebook!')"),
    ]

    nb['cells'] = cells

    with open("generated_notebook.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)



