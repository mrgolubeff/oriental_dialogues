FROM python:3.11-slim

WORKDIR /app

copy . .

RUN pip3 install --upgrade pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["python3", "bot.py"]

LABEL author='mrgolubeff'
