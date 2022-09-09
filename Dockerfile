FROM ubuntu as build

RUN apt-get update -y
RUN apt-get install -y python3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip install pyinstaller

COPY . .

RUN pyinstaller -D -F run.py

CMD cd dist; ls; ["run.exe"]

# FROM python:3-alpine

# WORKDIR /app

# COPY --from=build /app/dist .
# CMD ["run.exe"]