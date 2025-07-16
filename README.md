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
git clone https://github.com/pybrave/pipeline-metagenomics-metphlan-humann.git ~/.brave/pipeline/pipeline-metagenomics-metphlan-humann
```

进程间通讯的格式
```
echo '{"workflow_id": "wf-001", "workflow_event":"flow_begin", "ingress_event": "workflow_log"}' | socat - UNIX-CONNECT:/tmp/brave.sock
```