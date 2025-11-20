# Use an official web server 
FROM python:3.14-alpine

RUN mkdir -p /home/app 
# Copy HTML into container 
COPY ./src /home/app

#CMD ["python", "app.py"]