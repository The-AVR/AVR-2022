FROM node:lts-alpine

RUN apk update && apk add git

RUN npm install -g http-server

WORKDIR /app

RUN git -c http.sslVerify=False clone https://github.com/dbaldwin/DroneBlocks-Bell-AVR-Vue .

RUN npm install

RUN npm run build

EXPOSE 8080

CMD [ "http-server", "--proxy", "http://127.0.0.1:8080?", "dist" ]