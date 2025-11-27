from setuptools import setup, find_packages

setup(
    name="pybrave",
    version="0.2.4",
    packages=find_packages(),
    install_requires=[
        "fastapi", 
        "sqlalchemy",
        "pandas",
        "uvicorn[standard]",
        "typer",
        "pymysql",
        "click==8.1.8",
        "dependency-injector>=4.0,<5.0",
        "docker",
        "kubernetes",
        "psutil",
        "httpx",
        "nbformat",
        "PyMuPDF",
        "py2neo",
        "python-multipart",
        "aiofiles",
        "shortuuid",
        "aiohttp",
        "Bio",
        "nbconvert",
        "lxml",
        "cryptography",
        "openai",
        "oss2"
        ],
    entry_points={
        "console_scripts": [
            "brave = brave.__main__:app", 
        ]
    },
    project_urls={                             
        "Source": "https://github.com/pybrave/brave",
        "Tracker": "https://github.com/pybrave/brave",
        "Documentation": "https://github.com/pybrave/brave",
    },
    author="WangYang",
    description="Bioinformatics Reactive Analysis and Visualization Engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    package_data={
        "brave": [
            "frontend/**/*",  # 包含静态资源
            "frontend/build/**/*", 
            "pipeline/**/*",
            "templete/**/*",
            "cert/*.pem"
        ]
    },
)
