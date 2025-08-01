rm -rf brave/frontend/build
cp -r /ssd1/wy/workspace2/nextflow-react/dist brave/frontend/build


rm -rf dist/ build/ *.egg-info
python setup.py sdist bdist_wheel
twine upload dist/*
