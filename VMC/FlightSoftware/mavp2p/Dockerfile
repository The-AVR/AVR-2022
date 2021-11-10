FROM docker.io/library/alpine:3

WORKDIR /app

RUN apk add wget tar

RUN wget https://github.com/aler9/mavp2p/releases/download/v0.6.5/mavp2p_v0.6.5_linux_arm7.tar.gz \
 && tar -xvzf mavp2p*.tar.gz \
 && rm mavp2p*.tar.gz

COPY . .

CMD ["./docker-entrypoint.sh"]