from setuptools import setup, find_packages

setup(
    name="brave",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi", 
        "uvicorn[standard]",
        "click==8.1.8"
        ],
    entry_points={
        "console_scripts": [
            "brave = brave.__main__:app",  # 命令行入口
        ]
    },
    author="WangYang",
    description="Microbial Visualization Pipeline",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    package_data={
        "brave": [
            "frontend/**/*",  # 包含静态资源
            "pipeline/**/*"
        ]
    },
)
