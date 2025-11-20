## install
```
rm -rf brave/frontend/build
cp -r /ssd1/wy/workspace2/nextflow-react/dist brave/frontend/build


rm -rf dist/ build/ *.egg-info
python setup.py sdist bdist_wheel
twine upload dist/*
brave \
    --base-dir /ssd1/wy/workspace2/nextflow_workspace     \
    --work-dir /data/wangyang/nf_work     \
    --pipeline-dir /ssd1/wy/workspace2/nextflow-fastapi/pipeline-dev    \
    --db-type mysql --mysql-url root:123456@192.168.3.60:53306/brave1   \
    --port 5001
```


## Interprocess communication format
```
echo '{"workflow_id": "wf-001", "workflow_event":"flow_begin", "ingress_event": "workflow_log"}' | socat - UNIX-CONNECT:/tmp/brave.sock
```


install pipeline
```
git clone https://github.com/pybrave/pipeline-metagenomics.git ~/.brave/pipeline/7530139e-8985-423f-9fb6-32650828ca40

```

![](https://raw.githubusercontent.com/pybrave/brave/refs/heads/master/images/install.png)


```
brave --base-dir /ssd1/wy/workspace2/nextflow_workspace \
    --work-dir /data/wangyang/nf_work \
    --pipeline-dir /ssd1/wy/workspace2/nextflow-fastapi/pipeline-dev \
    --literature-dir /ssd1/wy/workspace2/nextflow-fastapi/literature \
    --db-type mysql --mysql-url root:123456@192.168.3.60:53306/pipeline  \
    --port 5000
```

## docker 
```
mkdir $PWD/data
docker run --rm -p 5000:5000  \
  --user $(id -u):$(id -g) \
  -v  /var/run/docker.sock:/var/run/docker.sock  \
  -v /tmp/brave.sock:/tmp/brave.sock \
  -v $PWD/data:/.brave \
  registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave

git clone https://github.com/pybrave/pipeline-metagenomics.git  $PWD/data/pipeline/7530139e-8985-423f-9fb6-32650828ca40
```
```
docker run --rm -p 5000:5000  \
  --user $(id -u):$(id -g) \
 --group-add $(stat -c '%g' /var/run/docker.sock) \
  -v  /var/run/docker.sock:/var/run/docker.sock  \
  -v /tmp/brave.sock:/tmp/brave.sock \
  -v ~/.brave:/.brave \
  -v /ssd1:/ssd1 \
  -v /data:/data \
  registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave \
  brave --pipeline-dir /ssd1/wy/workspace2/nextflow-fastapi/pipeline-dev \
  --base-dir /ssd1/wy/workspace2/nextflow_workspace \
  --work-dir /data/wangyang/nf_work \
  --literature-dir /ssd1/wy/workspace2/nextflow-fastapi/literature \
  --db-type mysql \
  --mysql-url root:123456@192.168.3.60:53306/pipeline \
  --port 5000 
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

```
docker network create traefik_proxy

docker run  \
  -p 8089:80 \
  -p 8087:8080 \
   --network traefik_proxy \
  -v $PWD/traefik.yml:/etc/traefik/traefik.yml \
  -v /var/run/docker.sock:/var/run/docker.sock \
  registry.cn-hangzhou.aliyuncs.com/wybioinfo/traefik:v3.5  

```
```

docker run  \
  -p 8089:80 \
  -p 8087:8080 \
   --network traefik_proxy \
  -v /var/run/docker.sock:/var/run/docker.sock \
  registry.cn-hangzhou.aliyuncs.com/wybioinfo/traefik:v3.5  \
  --api.insecure=true \
  --providers.docker=true \
  --log.level=DEBUG \
  --entrypoints.web.address=:80 

autossh -v  -N -R 5003:localhost:8089 master 
```
```
docker run --rm   \
  --name jupyter \
  --network traefik_proxy \
  -e NB_UID=$(id -u) \
  --label "traefik.enable=true" \
  --label 'traefik.http.routers.jupyter.rule=PathPrefix(`/jupyter`)' \
  --label "traefik.http.routers.jupyter.entrypoints=web" \
  --label "traefik.http.services.jupyter.loadbalancer.server.port=8888" \
    registry.cn-hangzhou.aliyuncs.com/wybioinfo/datascience-notebook:x86_64-ubuntu-22.04  \
    start.sh \
    jupyter notebook    --NotebookApp.password='' --NotebookApp.token='' --NotebookApp.base_url='/jupyter' 
```
```
docker run --rm   \
  --name rstudio \
  --network traefik_proxy \
  -e USERID=$(id -u) \
  -e DISABLE_AUTH=true \
  --label "traefik.enable=true" \
  --label 'traefik.http.routers.rstudio.rule=PathPrefix(`/rstudio`)' \
  --label "traefik.http.routers.rstudio.entrypoints=web" \
  --label "traefik.http.services.rstudio.loadbalancer.server.port=8787" \
  --label "traefik.http.middlewares.rstudio-strip.stripPrefix.prefixes=/rstudio" \
  --label "traefik.http.middlewares.rstudio-strip.stripPrefix.forceSlash=false" \
  --label "traefik.http.middlewares.rstudio-server-root-path-header.headers.customrequestheaders.X-RStudio-Root-Path=/rstudio" \
  --label "traefik.http.routers.rstudio.middlewares=rstudio-strip,rstudio-server-root-path-header" \
  registry.cn-hangzhou.aliyuncs.com/wybioinfo/maaslin2:1.22 /init 
```

```
docker run --rm -d \
    --publish=7474:7474 --publish=7687:7687 \
    --env=NEO4J_AUTH=none \
    --volume=$HOME/neo4j/data:/data \
    neo4j
```

```
docker network create opensearch-net
```
```
docker run   --rm  \
  --name opensearch-node \
  --network opensearch-net \
  -p 9200:9200 -p 9600:9600  \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:3
```
>   -e OPENSEARCH_INITIAL_ADMIN_PASSWORD=Zs.123456789 \
```
docker run -d --rm \
  --name opensearch-dashboards \
   --network opensearch-net \
  -p 5601:5601 \
  -e OPENSEARCH_HOSTS="http://opensearch-node:9200" \
  opensearchproject/opensearch-dashboards:latest
```

## contact
+ 1749748955@qq.com
