#FROM jjanzic/docker-python3-opencv:contrib-opencv-4.0.0
FROM python:3.7
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5555/tcp
EXPOSE 9000
COPY . .
CMD ["python", "server.py", "--use_wsgi"]