FROM ubuntu:20.04

WORKDIR /usr/src/vuln-api-app

COPY . .

RUN apt update -y
RUN apt install -y python3 python3-pip 

EXPOSE 3000
EXPOSE 22
EXPOSE 8080
EXPOSE 80

RUN pip3 install -r requirements.txt
CMD ["uvicorn","app:app"]