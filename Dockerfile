FROM python:3.10.18
RUN pip install pybrave
CMD ["brave"]

# docker build -t  registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave .
# docker run  --rm  -it -w $PWD -v $PWD:$PWD python:3.10.18 bash
# docker  build --build-arg http_proxy=http://127.0.0.1:7890 
# docker run  --rm   -v  /var/run/docker.sock:/var/run/docker.sock  -it -w $PWD -v $PWD:$PWD python:3.10.18 bash
# registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave