<p align="center">
  <img src="https://raw.githubusercontent.com/pybrave/brave/refs/heads/master/brave/frontend/img/logo.png" alt="brave" style="width: 500px;">
</p>
<p align="center" style="font-size: 1.5em;">
    <em>Bioinformatics Reactive Analysis and Visualization Engine</em>
</p>

<a href="https://pypi.org/project/pybrave" target="_blank">
    <img src="https://img.shields.io/pypi/v/pybrave?color=%2334D058&label=pypi%20package" alt="Package version">
</a>


BRAVE is a visual bioinformatics workflow platform, similar to Galaxy, that enables intuitive configuration and visualized execution of both upstream and downstream data analyses.

It provides an interactive interface that allows users to quickly develop upstream Nextflow analysis pipelines and downstream visualization scripts using containerized applications such as RStudio, VS Code, and Jupyter.

Once a Nextflow pipeline or visualization script is developed, it can be published to a GitHub repository as a BRAVE “store” app, allowing other analysts to download and use it. Each app maintains isolation, reproducibility, and scalability, leveraging containerized execution to ensure consistent and reliable analyses.



<p align="center">
  <img src="https://pybrave.github.io/brave-doc/assets/images/software_metaphlan-749e353b90a17c2a88106c3d04ce8177.gif" alt="brave" style="width: 500px;">
</p>


## Quick installation
```
curl -s https://raw.githubusercontent.com/pybrave/brave/refs/heads/master/install.sh  | bash
```
+ <http://localhost:5000>


Use Alibaba Cloud mirror
```
curl -s https://raw.githubusercontent.com/pybrave/brave/refs/heads/master/install.sh  | bash -s --  --aliyun
```

The default installation location is `$HOME/brave-install`, but you can specify the installation location using the `--base-dir` parameter.
```
curl -s https://raw.githubusercontent.com/pybrave/brave/refs/heads/master/install.sh  | bash -s --  --aliyun --base-dir /opt/brave
```


## pip Installation
```
pip install pybrave
```
```
brave
```
+ <http://localhost:5000>


## Docker
```
docker run --rm -it -p 5000:5000  \
     -v  /var/run/docker.sock:/var/run/docker.sock \
    wybioinfo/pybrave
```

>  registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave

## Docker + MySQL
```
docker network create brave-net
```
```
docker run  --rm -p 63306:3306 \
    --name brave-mysql \
     --network brave-net \
    -e MYSQL_ROOT_PASSWORD=123456  \
    -e LANG=C.UTF-8 \
    --shm-size=10G \
    -v /opt/brave/databases:/var/lib/mysql \
    -e MYSQL_DATABASE=brave \
    registry.cn-hangzhou.aliyuncs.com/wybioinfo/mysql:8.0.21 
    --default-authentication-plugin=mysql_native_password \
    --character-set-server=utf8mb4 \
    --lower-case-table-names=1 \
    --collation-server=utf8mb4_0900_ai_ci 
```
```
docker run --rm -it -p 5000:5000  \
    --network brave-net \
    -v  /var/run/docker.sock:/var/run/docker.sock \
    -v /opt/brave:/opt/brave \
    --user $(id -u):$(id -g) \
     --group-add $(stat -c '%g' /var/run/docker.sock) \
    wybioinfo/pybrave \
    brave --mysql-url root:123456@brave-mysql:3306/brave \
    --base-dir /opt/brave 
```
>    --use-https 

