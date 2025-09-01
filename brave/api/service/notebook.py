import nbformat as nbf
from nbconvert import PythonExporter



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


def convert_notebook(source_path, target_path):  
    # 读取 Notebook
    with open(source_path, "r", encoding="utf-8") as f:
        nb = nbf.read(f, as_version=4)

    # 创建 Python 导出器
    exporter = PythonExporter()
    python_code, _ = exporter.from_notebook_node(nb)

    # 写入 .py 文件
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(python_code)
        print(f"写入文件: {target_path}")