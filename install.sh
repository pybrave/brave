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