import nbformat as nbf



def generate_notebook(path):
    nb = nbf.v4.new_notebook()

    cells = [
        nbf.v4.new_markdown_cell("# 自动生成的 Notebook\n这里写一些说明"),
        nbf.v4.new_code_cell("import sys\nprint(sys.argv)"),
        nbf.v4.new_code_cell("print('Hello from generated notebook!')"),
    ]

    nb['cells'] = cells

    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)