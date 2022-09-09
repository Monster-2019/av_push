FROM python:3-alpine

RUN mkdir -p /app
WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

CMD python3 run.py