FROM python:3.11

ENV PYTHONUNBUFFERED=1 \
	GOOGLE_APPLICATION_CREDENTIALS=carea-project-5ba12d932822.json

WORKDIR /app

COPY . .

# 필요한 패키지 설치
RUN pip install --upgrade pip
USER root
RUN apt-get update && apt-get install -y portaudio19-dev
RUN pip install -r requirements.txt
