# Dockerfile
FROM python:3.9
EXPOSE 5000
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT ["bash", "run.sh"]