FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -y git python3-dev gcc

RUN apt-get install -y libglib2.0-0

RUN apt-get install -y libsm6 libxrender1 libfontconfig1

RUN rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt --upgrade

COPY app app

WORKDIR app

RUN python app.py

EXPOSE 5042-5100

CMD ["python", "app.py", "serve"]
