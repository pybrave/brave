FROM python:3.10.18
SHELL ["/bin/bash", "-c"]
ENV NVM_DIR=/root/.nvm
ENV NODE_VERSION=22.17.1
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && \
    source $NVM_DIR/nvm.sh && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION && \
    nvm use default && \
    npm install -g yarn

ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

RUN git clone --depth 1 https://github.com/pybrave/brave-ui.git /tmp/brave-ui
WORKDIR /tmp/brave-ui
RUN yarn install --frozen-lockfile && yarn build
RUN rm -rf /usr/local/share/.cache/yarn
WORKDIR /app
COPY . .
RUN mkdir -p /app/brave/frontend/build && \
    cp -r /tmp/brave-ui/dist/* /app/brave/frontend/build/


RUN pip install --no-cache-dir . 
RUN rm -rf /tmp/brave-ui


CMD ["brave"]
# docker build -t  registry.cn-hangzhou.aliyuncs.com/wybioinfo/brave .
# docker run  --rm  -it -w $PWD -v $PWD:$PWD python:3.10.18 bash
# docker  build --build-arg http_proxy=http://127.0.0.1:7890 
# docker run  --rm   -v  /var/run/docker.sock:/var/run/docker.sock  -it -w $PWD -v $PWD:$PWD python:3.10.18 bash
# registry.cn-hangzhou.aliyuncs.com/wybioinfo/pybrave