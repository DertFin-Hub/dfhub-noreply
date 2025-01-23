FROM python:3.10-slim
EXPOSE 587

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]