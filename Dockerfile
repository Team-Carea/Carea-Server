FROM python:3.11

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY . .

# 필요한 패키지 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
