# syntax=docker/dockerfile:1
FROM continuumio/miniconda3:latest
WORKDIR /app
COPY conda_packages.txt pip_packages.txt ./
RUN conda install --file conda_packages.txt --yes
RUN pip install -r pip_packages.txt

COPY spacebot_public_marketplace.csv app.py ./

CMD ["python", "app.py", "-p", $PORT]