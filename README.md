<p align="center">
  <img src="https://raw.githubusercontent.com/pybrave/brave/refs/heads/master/brave/frontend/img/logo.png" alt="brave" style="width: 500px;">
</p>
<p align="center" style="font-size: 1.5em;">
    <em>Bioinformatics Reactive Analysis and Visualization Engine</em>
</p>

<a href="https://pypi.org/project/pybrave" target="_blank">
    <img src="https://img.shields.io/pypi/v/pybrave?color=%2334D058&label=pypi%20package" alt="Package version">
</a>


## Installation
```
pip install pybrave
```

## Usage
```
brave
```
+ <http://localhost:5000>


install pipeline
```
git clone https://github.com/pybrave/pipeline-metagenomics.git ~/.brave/pipeline/7530139e-8985-423f-9fb6-32650828ca40

```

![](https://raw.githubusercontent.com/pybrave/brave/refs/heads/master/images/install.png)


## docker 
```
docker run --rm -p 5000:5000  -v  /var/run/docker.sock:/var/run/docker.sock  registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave
```

## development
```
mkdir -p development/pipeline-dev
mkdir -p development/base-dev 
python  -m brave \
   --port 5000 \
   --pipeline-dir development/pipeline-dev \
   --base-dir development/base-dev 
git clone https://github.com/pybrave/pipeline-metagenomics.git  development/pipeline-dev/7530139e-8985-423f-9fb6-32650828ca40
```

