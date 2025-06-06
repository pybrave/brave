docker run --rm --entrypoint=cat registry.cn-hangzhou.aliyuncs.com/wybioinfo/nginx /etc/nginx/nginx.conf > nginx.conf


docker run -d --rm --name react-nginx \
    -p 7878:80  \
    -v /ssd1/wy/workspace2/nextflow-react/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
    -v /ssd1/wy/workspace2/nextflow-react/dist:/usr/share/nginx/html \
    nginx 