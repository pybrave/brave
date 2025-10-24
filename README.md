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


## Docker
```
docker run --rm -it -p 5003:5000  \
     -v  /var/run/docker.sock:/var/run/docker.sock \
    wybioinfo/pybrave
```

```
docker run --rm -it -p 5003:5000  \
     -v  /var/run/docker.sock:/var/run/docker.sock \
    registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave
```

